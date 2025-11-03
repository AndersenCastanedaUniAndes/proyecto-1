from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, Depends
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, date
from fastapi.security import OAuth2PasswordBearer
from app.models.databases import Base
from config.config import DATABASE_URL, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.models import models
from typing import List, Optional
import pandas as pd

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
        print("Creando tablas en la base de datos...")
        print(f"URL de BD: {DATABASE_URL}")
        Base.metadata.create_all(bind=engine)
        print("Tablas creadas correctamente")

        # Verificar que las tablas existen
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"Tablas disponibles: {tables}")

    except Exception as e:
        print(f"Error al crear tablas: {str(e)}")
        raise e


# =====================================================
# CRUD para la entidad VENTAS
# =====================================================

def get_venta(db: Session, venta_id: int) -> Optional[models.Venta]:
    """
    /**
     * @brief Obtiene una venta por su ID.
     * @param db Sesión de base de datos.
     * @param venta_id Identificador de la venta.
     * @return Venta encontrada o None si no existe.
     */
    """
    return db.query(models.Venta).filter(models.Venta.id == venta_id).first()


def get_ventas(db: Session, skip: int = 0, limit: int = 100) -> List[models.Venta]:
    """
    /**
     * @brief Obtiene la lista de ventas.
     * @param db Sesión de base de datos.
     * @param skip y limit para paginación.
     * @return Ventas encontradas o lista vacía si no existen.
     */
    """
    return db.query(models.Venta).offset(skip).limit(limit).all()


def create_venta(db: Session, venta) -> models.Venta:
    """
    /**
     * @brief Crea una nueva venta en la base de datos.
     * @param db Sesión de base de datos.
     * @param venta Objeto con los datos de la venta.
     * @return Venta creada.
     */
    """
    fecha_venta = getattr(venta, "fecha", None) or date.today()

    db_obj = models.Venta(
        fecha=fecha_venta,
        vendedor=venta.vendedor,
        vendedorId=venta.vendedorId,
        producto=venta.producto,
        producto_id=venta.producto_id,
        cantidad=venta.cantidad,
        valorUnitario=venta.valorUnitario,
        valorTotal=venta.valorTotal,
        cliente=venta.cliente,
        comision=venta.comision
    )

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_venta(db: Session, db_venta: models.Venta, venta_in) -> models.Venta:
    """
    /**
     * @brief Actualiza los datos de una venta existente.
     * @param db Sesión de base de datos.
     * @param db_venta Venta existente en la BD.
     * @param venta_in Objeto con los nuevos valores.
     * @return Venta actualizada.
     */
    """
    for field, value in venta_in.dict().items():
        setattr(db_venta, field, value)
    db.commit()
    db.refresh(db_venta)
    return db_venta


def delete_venta(db: Session, db_venta: models.Venta):
    """
    /**
     * @brief Elimina una venta de la base de datos.
     * @param db Sesión de base de datos.
     * @param db_venta Venta a eliminar.
     */
    """
    db.delete(db_venta)
    db.commit()
    return
