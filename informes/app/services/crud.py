from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, Depends
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, date
from fastapi.security import OAuth2PasswordBearer
from app.models.database import engine, Base
from app.models.models import DBVisita
from app.models.ventas import VentaCreate
from app.models.visitas import VisitaBase, VisitaCreate
from config.config import DATABASE_URL, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.models import models
from typing import List, Optional
import pandas as pd

# Configuración de encriptación
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración de OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


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


def create_venta(db: Session, venta: VentaCreate) -> models.Venta:
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
        vendedor_id=venta.vendedor_id,
        productos=[p.dict() for p in venta.productos],
        cliente=venta.cliente,
        cliente_id=venta.cliente_id,
        comision=venta.comision,
        estado="Pendiente"
    )

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_ventas_vendedor(db: Session, vendedor_id: int, skip: int = 0, limit: int = 100) -> List[models.Venta]:
    """
    /**
     * @brief Obtiene la lista de ventas de un vendedor específico.
     * @param db Sesión de base de datos.
     * @param vendedor_id Identificador del vendedor.
     * @param skip y limit para paginación.
     * @return Ventas encontradas o lista vacía si no existen.
     */
    """
    return db.query(models.Venta).filter(models.Venta.vendedor_id == vendedor_id).offset(skip).limit(limit).all()


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


# =====================================================
# CRUD para la entidad VISITAS
# =====================================================

def create_visita(db: Session, visita: VisitaCreate) -> models.DBVisita:
    fecha_hora = datetime.strptime(
        f"{visita.fecha} {visita.hora}",
        "%Y-%m-%d %I:%M %p"
    )

    db_obj: DBVisita = DBVisita(
        cliente=visita.cliente,
        cliente_id=visita.cliente_id,
        vendedor=visita.vendedor,
        vendedor_id=visita.vendedor_id,
        fecha=fecha_hora,
        direccion=visita.direccion,
        hallazgos=visita.hallazgos,
        sugerencias=visita.sugerencias
    )

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_visitas(vendedor_id: int, db: Session, skip: int = 0, limit: int = 100) -> List[VisitaBase]:
    visitas: List[DBVisita] = db.query(DBVisita).filter(DBVisita.vendedor_id == vendedor_id).offset(skip).limit(limit).all()
    response = [
        {
            "id": visita.id,
            "cliente": visita.cliente,
            "cliente_id": visita.cliente_id,
            "vendedor": visita.vendedor,
            "vendedor_id": visita.vendedor_id,
            "fecha": visita.fecha.strftime("%Y-%m-%d") if visita.fecha else None,
            "hora": visita.fecha.strftime("%I:%M %p") if visita.fecha else None,
            "direccion": visita.direccion,
            "hallazgos": visita.hallazgos,
            "sugerencias": visita.sugerencias
        }
        for visita in visitas
    ]

    return response
