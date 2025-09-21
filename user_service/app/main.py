from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST
from app.services.user_service import init_db
from app.routes import user_routes

from app.middleware.jwt_middleware import JWTMiddleware, get_metrics

app = FastAPI()

app.add_middleware(JWTMiddleware)


@app.on_event("startup")
async def on_startup():
    print("🚀 Iniciando aplicación...")
    try:
        # Inicializar la base de datos y crear tablas
        print("📊 Inicializando base de datos...")
        init_db()
        print("✅ Base de datos inicializada correctamente")
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

# 👇 expón /metrics con el registry por defecto
@app.get("/metrics")
def metrics():
    return Response(get_metrics(), media_type=CONTENT_TYPE_LATEST)

# (opcional) health
@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(user_routes.router)

@app.get("/")
def read_root():
    return {"Hello": "User Service"}

app.include_router(user_routes.router)

@app.get("/")
def read_root():
    return {"Hello": "User Service"}
