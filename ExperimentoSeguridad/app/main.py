"""
FastAPI application for Experimento Seguridad JWT + RBAC microservice.
"""
import logging
from datetime import datetime

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from app.config import METRICS_PATH, PROMETHEUS_ENABLED
from app.middleware.jwt_middleware import JWTMiddleware, get_metrics, get_redis_status
from app.routes import user_routes
from app.services.user_service import init_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Experimento Seguridad JWT + RBAC",
    description="API with JWT RS256, RBAC and token revocation for availability experiments",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT middleware with metrics
app.add_middleware(JWTMiddleware)


@app.on_event("startup")
async def on_startup():
    """Application startup event."""
    logger.info("🚀 Starting application...")
    try:
        # Initialize database and create tables
        logger.info("📊 Initializing database...")
        init_db()
        logger.info("✅ Database initialized successfully")

        # Check Redis status
        redis_status = get_redis_status()
        logger.info(f"🔴 Redis status: {redis_status}")

    except Exception as e:
        logger.error(f"❌ Error initializing database: {str(e)}")
        raise e


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Global handler for 422 validation errors."""
    return JSONResponse(
        status_code=422,
        content={
            "message": "Data validation error",
            "errors": exc.errors(),
        },
    )


# Include routes
app.include_router(user_routes.router)


@app.get("/")
def read_root():
    """Root endpoint."""
    return {
        "service": "Experimento Seguridad JWT + RBAC",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics",
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    redis_status = get_redis_status()
    return {
        "status": "healthy",
        "redis": redis_status,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@app.get(METRICS_PATH)
def metrics():
    """Prometheus metrics endpoint."""
    if not PROMETHEUS_ENABLED:
        return {"error": "Prometheus disabled"}

    metrics_data = get_metrics()
    return Response(
        content=metrics_data,
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )


@app.post("/dbg/metric")
def dbg_metric():
    """Debug endpoint to test metrics."""
    from app.middleware.jwt_middleware import smoke_counter

    smoke_counter.inc()
    return {"ok": True}