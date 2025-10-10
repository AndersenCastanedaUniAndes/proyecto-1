from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, Depends
from pydantic import ValidationError
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.models.databases import Base
from config.config import DATABASE_URL, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from sqlalchemy.orm import Session
from app.models import models, producto
from typing import List, Optional

# Configuración de BD
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Configuración de encriptación
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración de OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Dependencia para obtener la DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Crear las tablas en la base de datos
def init_db():
    try:
        print("🔧 Creando tablas en la base de datos...")
        print(f"📊 URL de BD: {DATABASE_URL}")
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas correctamente")
        
        # Verificar que las tablas existen
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"📋 Tablas disponibles: {tables}")
        
    except Exception as e:
        print(f"❌ Error al crear tablas: {str(e)}")
        raise e

# Manejo de contraseñas
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Crear token JWT
def create_access_token(data: dict, expires_delta: timedelta = None):
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        
        to_encode.update({"exp": expire})
        #print("-----222222222------")
        #print(jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM))

        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear el token: {str(e)}")


# CRUD básico

def get_producto(db: Session, producto_id: int) -> Optional[models.Producto]:
    return db.query(models.Producto).filter(models.Producto.id == producto_id).first()


def get_producto_by_serial(db: Session, numeroSerial: str) -> Optional[models.Producto]:
    return db.query(models.Producto).filter(models.Producto.numeroSerial == numeroSerial).first()


def get_productos(db: Session, skip: int = 0, limit: int = 100) -> List[models.Producto]:
    return db.query(models.Producto).offset(skip).limit(limit).all()


def create_producto(db: Session, producto) -> models.Producto:
    db_obj = models.Producto(
        nombre=producto.nombre,
        lote=producto.lote,
        numeroSerial=producto.numeroSerial,
        proveedor=producto.proveedor,
        precioUnidad=producto.precioUnidad,
        precioTotal=producto.precioTotal,
        paisOrigen=producto.paisOrigen,
        uom=producto.uom,
        cantidad=producto.cantidad,
        tipoAlmacenamiento=producto.tipoAlmacenamiento,
        temperaturaMin=producto.temperaturaMin,
        temperaturaMax=producto.temperaturaMax,
        fechaCreacion = producto.fechaCreacion if hasattr(producto, 'fechaCreacion') else __import__('datetime').datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_producto(db: Session, db_producto: models.Producto, producto_in: models.Producto) -> models.Producto:
    for field, value in producto_in.dict().items():
        setattr(db_producto, field, value)
    db.commit()
    db.refresh(db_producto)
    return db_producto


def delete_producto(db: Session, db_producto: models.Producto):
    db.delete(db_producto)
    db.commit()
    return

