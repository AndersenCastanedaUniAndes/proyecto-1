from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware

from app.services.user_service import init_db
from app.routes import user_routes
from app.middleware.jwt_middleware import JWTMiddleware, get_metrics, get_redis_status
from config.config import PROMETHEUS_ENABLED, METRICS_PATH

app = FastAPI(
    title="Experimento Seguridad JWT + RBAC",
    description="API con JWT RS256, RBAC y revocación para experimento de disponibilidad",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware JWT con métricas
app.add_middleware(JWTMiddleware)

@app.on_event("startup")
async def on_startup():
    print("🚀 Iniciando aplicación...")
    try:
        # Inicializar la base de datos y crear tablas
        print("📊 Inicializando base de datos...")
        init_db()
        print("✅ Base de datos inicializada correctamente")
        
        # Verificar estado de Redis
        redis_status = get_redis_status()
        print(f"🔴 Estado Redis: {redis_status}")
        
    except Exception as e:
        print(f"❌ Error al inicializar BD: {str(e)}")
        raise e

# Handler global para 422
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "message": "Error en la validación de datos",
            "errors": exc.errors()
        },
    )

# Incluir rutas
app.include_router(user_routes.router)

@app.get("/")
def read_root():
    return {
        "service": "Experimento Seguridad JWT + RBAC",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    redis_status = get_redis_status()
    return {
        "status": "healthy",
        "redis": redis_status,
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.get(METRICS_PATH)
def metrics():
    """Endpoint de métricas Prometheus"""
    if not PROMETHEUS_ENABLED:
        return {"error": "Prometheus deshabilitado"}
    
    metrics_data = get_metrics()
    return Response(
        content=metrics_data,
        media_type="text/plain; version=0.0.4; charset=utf-8"
    )
