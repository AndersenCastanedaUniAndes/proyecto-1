from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.responses import JSONResponse

from app.services.crud import init_db
from app.routes import routes
from app.routes.routes import router

app = FastAPI( title="API de Productos",
            description="API para gestionar productos",
            version="1.0.0")
app.include_router(router, prefix="/productos", tags=["Productos"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Puerto de tu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

app.include_router(routes.router)

@app.get("/")
def read_root():
    return {"Hello": "Products Service"}
