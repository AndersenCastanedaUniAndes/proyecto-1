"""
/**
 * @file crud.py
 * @brief Módulo CRUD principal para la gestión de proveedores en la base de datos.
 *
 * Este módulo implementa operaciones básicas de persistencia sobre la entidad Proveedor,
 * así como utilidades complementarias para la inicialización de la base de datos, manejo
 * de contraseñas, autenticación mediante JWT.
 *
 * <p><b>Tecnologías utilizadas:</b></p>
 * - FastAPI
 * - SQLAlchemy ORM
 * - Passlib (bcrypt)
 * - JOSE (JWT)
 * - Pandas
 *
 * <p><b>Autor:</b> Equipo de Desarrollo Grupo 1</p>
 * <p><b>Versión:</b> 1.0</p>
 * <p><b>Fecha:</b> 2025-10-20</p>
 */
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import UploadFile, File,HTTPException, Depends
from pydantic import ValidationError
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.models.database import Base, engine
from config.config import DATABASE_URL, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from sqlalchemy.orm import Session
from app.models import models
from typing import List, Optional
from datetime import datetime
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



# CRUD básico

def get_proveedor(db: Session, proveedor_id: int) -> Optional[models.Proveedor]:
    """
    /**
     * @brief Obtiene un proveedor por su ID.
     * @param db Sesión de base de datos.
     * @param proveedor_id Identificador del proveedor.
     * @return Proveedor encontrado o None si no existe.
     */
    """
    return db.query(models.Proveedor).filter(models.Proveedor.id == proveedor_id).first()




def get_proveedores(db: Session, skip: int = 0, limit: int = 100) -> List[models.Proveedor]:
    """
    /**
     * @brief Obtiene la lista de proveedores.
     * @param db Sesión de base de datos.
     * @param skipy limit para paginacion.
     * @return Proveedores encontrados o None si no existe.
     */
    """
    return db.query(models.Proveedor).offset(skip).limit(limit).all()


from typing import List



def create_proveedor(db: Session, proveedor) -> models.Proveedor:
    """
    Crea un nuevo proveedor en la base de datos.

    Args:
        db (Session): Sesión de base de datos.
        proveedor: Objeto con los datos del proveedor a insertar.

    Returns:
        models.Proveedor: Proveedor creado en la base de datos.
    """

    # Si no se proporciona fechaCreacion, se usa la actual con hora, minuto y segundo
    fecha_creacion = getattr(proveedor, "fechaCreacion", None) or datetime.now()

    db_obj = models.Proveedor(
        nombre=proveedor.nombre,
        correoElectronico=proveedor.correoElectronico,
        estado=proveedor.estado,
        fechaCreacion=fecha_creacion
    )

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_proveedor(db: Session, db_proveedor: models.Proveedor, proveedor_in: models.Proveedor) -> models.Proveedor:
    """
    /**
     * @brief Actualiza los datos de un proveedor existente.
     * @param db Sesión de base de datos.
     * @param db_proveedor Proveedor existente en la BD.
     * @param proveedor_in Objeto con los nuevos valores.
     * @return Proveedor actualizado.
     */
    """
    
    for field, value in proveedor_in.dict().items():
        setattr(db_proveedor, field, value)
    db.commit()
    db.refresh(db_proveedor)
    return db_proveedor


def delete_proveedor(db: Session, db_proveedor: models.Proveedor):
    """
    /**
     * @brief Elimina un proveedor de la base de datos.
     * @param db Sesión de base de datos.
     * @param db_proveedor Proveedor a eliminar.
     */
    """
    db.delete(db_proveedor)
    db.commit()
    return

