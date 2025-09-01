from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.services.user_service import init_db
from app.routes import user_routes

app = FastAPI()

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

app.include_router(user_routes.router)

@app.get("/")
def read_root():
    return {"Hello": "User Service"}
