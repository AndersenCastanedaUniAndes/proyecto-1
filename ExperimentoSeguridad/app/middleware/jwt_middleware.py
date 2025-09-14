"""
Middleware JWT con métricas Prometheus para observabilidad
"""
import time
import logging
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import jwt as pyjwt
from datetime import datetime, timedelta

from app.utils.auth import verify_token
from app.utils.revocation_store import revocation_store
from app.utils.rbac import rbac_manager
from config.config import JWT_ISS, JWT_AUD, SKEW_SECONDS

# Configurar logging
logger = logging.getLogger(__name__)

# Métricas Prometheus
try:
    from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
    PROMETHEUS_AVAILABLE = True
    
    # Métricas de validación JWT
    jwt_validation_seconds = Histogram(
        'jwt_validation_seconds',
        'Tiempo de validación JWT en segundos',
        ['endpoint', 'method'],
        unit='seconds'
    )
    
    jwt_validation_failures_total = Counter(
        'jwt_validation_failures_total',
        'Total de fallos en validación JWT',
        ['reason', 'endpoint']
    )
    
    jwt_validation_success_total = Counter(
        'jwt_validation_success_total',
        'Total de validaciones JWT exitosas',
        ['endpoint']
    )
    
    active_tokens_gauge = Gauge(
        'active_tokens_total',
        'Total de tokens activos'
    )
    
    redis_connection_status = Gauge(
        'redis_connection_status',
        'Estado de conexión Redis (1=conectado, 0=desconectado)'
    )
    
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logger.warning("Prometheus no disponible. Métricas deshabilitadas.")

class JWTMiddleware(BaseHTTPMiddleware):
    """Middleware JWT con métricas y validación completa"""
    
    def __init__(self, app: ASGIApp, skip_paths: Optional[list] = None):
        super().__init__(app)
        self.skip_paths = skip_paths or [
            "/",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/.well-known/jwks.json",
            "/metrics",
            "/health"
        ]
    
    async def dispatch(self, request: Request, call_next):
        """Procesa la request con validación JWT"""
        
        # Verificar si debe saltar la validación
        if self._should_skip_validation(request):
            return await call_next(request)
        
        # Iniciar medición de tiempo
        start_time = time.time()
        
        try:
            # Extraer token del header Authorization
            token = self._extract_token(request)
            if not token:
                self._record_failure("no_token", request.url.path)
                return self._unauthorized_response("Token de autorización requerido")
            
            # Validar token JWT
            payload = await self._validate_jwt_token(token, request)
            
            # Verificar revocación
            if await self._is_token_revoked(payload.get("jti"), request):
                self._record_failure("token_revoked", request.url.path)
                return self._unauthorized_response("Token revocado")
            
            # Verificar permisos RBAC
            if not await self._check_rbac_permissions(payload, request):
                self._record_failure("insufficient_permissions", request.url.path)
                return self._forbidden_response("Permisos insuficientes")
            
            # Agregar información del usuario a la request
            request.state.user_payload = payload
            request.state.user_role = payload.get("role")
            request.state.user_email = payload.get("sub")
            
            # Registrar éxito
            self._record_success(request.url.path)
            
            # Procesar request
            response = await call_next(request)
            
            # Calcular tiempo de validación
            validation_time = time.time() - start_time
            self._record_validation_time(request.url.path, request.method, validation_time)
            
            return response
            
        except HTTPException as e:
            self._record_failure("http_exception", request.url.path)
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail}
            )
        except Exception as e:
            logger.error(f"Error en middleware JWT: {e}")
            self._record_failure("internal_error", request.url.path)
            return self._internal_error_response("Error interno del servidor")
    
    def _should_skip_validation(self, request: Request) -> bool:
        """Verifica si debe saltar la validación JWT"""
        return any(request.url.path.startswith(path) for path in self.skip_paths)
    
    def _extract_token(self, request: Request) -> Optional[str]:
        """Extrae el token del header Authorization"""
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        return auth_header[7:]  # Remover "Bearer "
    
    async def _validate_jwt_token(self, token: str, request: Request) -> Dict[str, Any]:
        """Valida el token JWT con validaciones completas"""
        try:
            # Decodificar header para obtener kid
            unverified_header = pyjwt.get_unverified_header(token)
            kid = unverified_header.get("kid")
            
            if not kid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido: no contiene kid"
                )
            
            # Obtener clave pública
            from app.utils.key_manager import key_manager
            public_key_pem = key_manager.get_public_key_pem(kid)
            
            # Decodificar con validaciones completas
            payload = pyjwt.decode(
                token,
                public_key_pem,
                algorithms=["RS256"],
                issuer=JWT_ISS,
                audience=JWT_AUD,
                leeway=SKEW_SECONDS  # Tolerancia de ±60s
            )
            
            # Validaciones adicionales
            if not payload.get("sub"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido: no contiene subject"
                )
            
            if not payload.get("role"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido: no contiene role"
                )
            
            return payload
            
        except pyjwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado"
            )
        except pyjwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token inválido: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error validando JWT: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno validando token"
            )
    
    async def _is_token_revoked(self, jti: str, request: Request) -> bool:
        """Verifica si el token está revocado"""
        try:
            # Obtener sesión de DB (simplificado para el middleware)
            from app.services.user_service import get_db
            db = next(get_db())
            
            try:
                return revocation_store.is_token_revoked(jti, db)
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error verificando revocación: {e}")
            return True  # Fail-closed
    
    async def _check_rbac_permissions(self, payload: Dict[str, Any], request: Request) -> bool:
        """Verifica permisos RBAC para el endpoint"""
        try:
            role = payload.get("role")
            if not role:
                return False
            
            # Mapear endpoint a recurso y acción
            resource, action = self._map_endpoint_to_permission(request)
            if not resource or not action:
                return True  # Si no se puede mapear, permitir (endpoints públicos)
            
            return rbac_manager.has_permission(role, resource, action)
            
        except Exception as e:
            logger.error(f"Error verificando RBAC: {e}")
            return False
    
    def _map_endpoint_to_permission(self, request: Request) -> tuple:
        """Mapea endpoint HTTP a recurso y acción RBAC"""
        path = request.url.path
        method = request.method
        
        # Mapeo de endpoints a permisos
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
    
    def _record_failure(self, reason: str, endpoint: str):
        """Registra fallo en métricas"""
        if PROMETHEUS_AVAILABLE:
            jwt_validation_failures_total.labels(reason=reason, endpoint=endpoint).inc()
    
    def _record_success(self, endpoint: str):
        """Registra éxito en métricas"""
        if PROMETHEUS_AVAILABLE:
            jwt_validation_success_total.labels(endpoint=endpoint).inc()
    
    def _record_validation_time(self, endpoint: str, method: str, duration: float):
        """Registra tiempo de validación"""
        if PROMETHEUS_AVAILABLE:
            jwt_validation_seconds.labels(endpoint=endpoint, method=method).observe(duration)
    
    def _unauthorized_response(self, detail: str) -> JSONResponse:
        """Respuesta 401"""
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": detail},
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    def _forbidden_response(self, detail: str) -> JSONResponse:
        """Respuesta 403"""
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": detail}
        )
    
    def _internal_error_response(self, detail: str) -> JSONResponse:
        """Respuesta 500"""
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": detail}
        )

def get_metrics():
    """Obtiene métricas de Prometheus"""
    if PROMETHEUS_AVAILABLE:
        return generate_latest()
    return b"# Prometheus no disponible\n"

def get_redis_status():
    """Obtiene estado de Redis"""
    if PROMETHEUS_AVAILABLE:
        status = revocation_store.get_redis_status()
        redis_connection_status.set(1 if status["available"] else 0)
        return status
    return {"available": False, "status": "prometheus_disabled"}
