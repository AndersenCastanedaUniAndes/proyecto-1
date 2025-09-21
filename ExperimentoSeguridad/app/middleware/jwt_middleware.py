"""
JWT Middleware with Prometheus metrics for observability.
"""
import logging
import time
from typing import Any, Dict, Optional

import jwt as pyjwt
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.config import JWT_AUD, JWT_ISS, PROMETHEUS_MULTIPROC_DIR, SKEW_SECONDS
from app.utils.auth import verify_token
from app.utils.rbac import rbac_manager
from app.utils.revocation_store import revocation_store

logger = logging.getLogger(__name__)

# Prometheus metrics
try:
    from prometheus_client import (
        CONTENT_TYPE_LATEST,
        Counter,
        Gauge,
        Histogram,
        MultiProcessCollector,
        generate_latest,
        CollectorRegistry,
    )

    PROMETHEUS_AVAILABLE = True

    # Create registry for multiprocess support
    if PROMETHEUS_MULTIPROC_DIR:
        registry = CollectorRegistry()
        MultiProcessCollector(registry)
    else:
        registry = None

    # JWT validation metrics
    jwt_validation_seconds = Histogram(
        "jwt_validation_seconds",
        "JWT validation time in seconds",
        ["route_path", "method"],
        unit="seconds",
        registry=registry,
    )

    jwt_validation_failures_total = Counter(
        "jwt_validation_failures_total",
        "Total JWT validation failures",
        ["reason", "route_path"],
        registry=registry,
    )

    jwt_validation_success_total = Counter(
        "jwt_validation_success_total",
        "Total successful JWT validations",
        ["route_path"],
        registry=registry,
    )

    redis_connection_status = Gauge(
        "redis_connection_status",
        "Redis connection status (1=connected, 0=disconnected)",
        registry=registry,
    )

except ImportError:
    PROMETHEUS_AVAILABLE = False
    logger.warning("Prometheus not available. Metrics disabled.")


class JWTMiddleware(BaseHTTPMiddleware):
    """JWT Middleware with comprehensive validation and metrics."""

    def __init__(self, app: ASGIApp, skip_paths: Optional[list] = None):
        super().__init__(app)
        # Exact public routes
        self.skip_exact = {"/", "/metrics", "/health", "/openapi.json", "/token"}
        # Public prefixes (docs/UI, JWKS)
        self.skip_prefixes = ("/docs", "/redoc", "/.well-known")

    def _should_skip_validation(self, request: Request) -> bool:
        """Check if request should skip JWT validation."""
        path = request.url.path
        if path in self.skip_exact:
            return True
        return any(path.startswith(prefix) for prefix in self.skip_prefixes)

    async def dispatch(self, request: Request, call_next):
        """Process request with JWT validation."""
        if self._should_skip_validation(request):
            return await call_next(request)

        start_time = time.perf_counter()
        route_path = self._get_route_path(request)

        try:
            # Extract token from Authorization header
            token = self._extract_token(request)
            if not token:
                self._record_failure("no_token", route_path)
                return self._unauthorized_response("Authorization token required")

            # Validate JWT token
            payload = await self._validate_jwt_token(token, request)

            # Check token revocation
            if await self._is_token_revoked(payload.get("jti"), request):
                self._record_failure("token_revoked", route_path)
                return self._unauthorized_response("Token revoked")

            # Check RBAC permissions
            if not await self._check_rbac_permissions(payload, request):
                self._record_failure("insufficient_permissions", route_path)
                return self._forbidden_response("Insufficient permissions")

            # Add user information to request state
            request.state.user_payload = payload
            request.state.user_role = payload.get("role")
            request.state.user_email = payload.get("sub")

            self._record_success(route_path)
            return await call_next(request)

        except HTTPException as e:
            self._record_failure("http_exception", route_path)
            return JSONResponse(
                status_code=e.status_code, content={"detail": e.detail}
            )
        except Exception as e:
            logger.error(f"JWT middleware error: {e}")
            self._record_failure("internal_error", route_path)
            return self._internal_error_response("Internal server error")
        finally:
            # Record validation time in finally block
            duration = time.perf_counter() - start_time
            self._record_validation_time(route_path, request.method, duration)

    def _get_route_path(self, request: Request) -> str:
        """Get route path for metrics (avoid high cardinality)."""
        path = request.url.path
        # Normalize paths to avoid high cardinality
        if path.startswith("/users/"):
            return "/users/{user_id}"
        elif path.startswith("/auth/"):
            return "/auth/*"
        return path

    def _extract_token(self, request: Request) -> Optional[str]:
        """Extract token from Authorization header."""
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        return auth_header[7:]  # Remove "Bearer "

    async def _validate_jwt_token(self, token: str, request: Request) -> Dict[str, Any]:
        """Validate JWT token with comprehensive checks."""
        try:
            # Decode header to get kid
            unverified_header = pyjwt.get_unverified_header(token)
            kid = unverified_header.get("kid")

            if not kid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing kid",
                )

            # Get public key
            from app.utils.key_manager import key_manager

            public_key_pem = key_manager.get_public_key_pem(kid)

            # Decode with comprehensive validations
            payload = pyjwt.decode(
                token,
                public_key_pem,
                algorithms=["RS256"],
                issuer=JWT_ISS,
                audience=JWT_AUD,
                leeway=SKEW_SECONDS,  # ±60s tolerance
            )

            # Additional validations
            if not payload.get("sub"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing subject",
                )

            if not payload.get("role"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing role",
                )

            return payload

        except pyjwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
            )
        except pyjwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}",
            )
        except Exception as e:
            logger.error(f"JWT validation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal error validating token",
            )

    async def _is_token_revoked(self, jti: str, request: Request) -> bool:
        """Check if token is revoked using the same function as services."""
        try:
            # Use the same database function as services
            from app.services.user_service import get_db

            db = next(get_db())
            try:
                return revocation_store.is_token_revoked(jti, db)
            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error checking token revocation: {e}")
            return True  # Fail-closed

    async def _check_rbac_permissions(self, payload: Dict[str, Any], request: Request) -> bool:
        """Check RBAC permissions for the endpoint."""
        try:
            role = payload.get("role")
            if not role:
                return False

            # Map endpoint to resource and action
            resource, action = self._map_endpoint_to_permission(request)
            if not resource or not action:
                return True  # Allow if cannot map (public endpoints)

            return rbac_manager.has_permission(role, resource, action)

        except Exception as e:
            logger.error(f"RBAC permission check error: {e}")
            return False

    def _map_endpoint_to_permission(self, request: Request) -> tuple:
        """Map HTTP endpoint to RBAC resource and action."""
        path = request.url.path
        method = request.method

        # Map endpoints to permissions
        if path.startswith("/users"):
            if method == "GET":
                return "users", "read"
            elif method == "POST":
                return "users", "create"
            elif method == "PUT":
                return "users", "update"
            elif method == "DELETE":
                return "users", "delete"

        elif path.startswith("/auth"):
            if "rotate-keys" in path:
                return "auth", "rotate_keys"
            elif "blacklist" in path:
                return "auth", "view_blacklist"

        return None, None

    def _record_failure(self, reason: str, route_path: str):
        """Record failure in metrics."""
        if PROMETHEUS_AVAILABLE:
            jwt_validation_failures_total.labels(
                reason=reason, route_path=route_path
            ).inc()

    def _record_success(self, route_path: str):
        """Record success in metrics."""
        if PROMETHEUS_AVAILABLE:
            jwt_validation_success_total.labels(route_path=route_path).inc()

    def _record_validation_time(self, route_path: str, method: str, duration: float):
        """Record validation time."""
        if PROMETHEUS_AVAILABLE:
            jwt_validation_seconds.labels(
                route_path=route_path, method=method
            ).observe(duration)

    def _unauthorized_response(self, detail: str) -> JSONResponse:
        """401 Unauthorized response."""
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": detail},
            headers={"WWW-Authenticate": "Bearer"},
        )

    def _forbidden_response(self, detail: str) -> JSONResponse:
        """403 Forbidden response."""
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content={"detail": detail}
        )

    def _internal_error_response(self, detail: str) -> JSONResponse:
        """500 Internal Server Error response."""
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": detail},
        )


def get_metrics():
    """Get Prometheus metrics."""
    if PROMETHEUS_AVAILABLE:
        if PROMETHEUS_MULTIPROC_DIR:
            return generate_latest(registry)
        return generate_latest()
    return b"# Prometheus not available\n"


def get_redis_status():
    """Get Redis status."""
    if PROMETHEUS_AVAILABLE:
        status = revocation_store.get_redis_status()
        redis_connection_status.set(1 if status["available"] else 0)
        return status
    return {"available": False, "status": "prometheus_disabled"}