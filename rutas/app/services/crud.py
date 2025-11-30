from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from app.models import models
from sqlalchemy import create_engine
from config.config import DATABASE_URL, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.models.databases import Base

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



# ===============================================================
# 📦 CRUD PEDIDO
# ===============================================================
def get_pedido(db: Session, pedido_id: int) -> Optional[models.Pedido]:
    return db.query(models.Pedido).filter(models.Pedido.id == pedido_id).first()


def get_pedidos(db: Session, skip: int = 0, limit: int = 100) -> List[models.Pedido]:
    return db.query(models.Pedido).offset(skip).limit(limit).all()


def create_pedido(db: Session, pedido) -> models.Pedido:
    db_obj = models.Pedido(
        cliente=pedido.cliente,
        direccion=pedido.direccion,
        latitud=pedido.latitud,
        longitud=pedido.longitud,
        volumen=pedido.volumen,
        peso=pedido.peso,
        ventana_inicio=pedido.ventanaInicio,
        ventana_fin=pedido.ventanaFin,
        productos=",".join(pedido.productos),
        valor=pedido.valor,
        seleccionado=pedido.seleccionado,
        fecha_creacion=datetime.now()
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_pedido(db: Session, db_pedido: models.Pedido, pedido_in) -> models.Pedido:
    for field, value in pedido_in.dict().items():
        if field == "productos":
            value = ",".join(value)
        setattr(db_pedido, field if field not in ["ventanaInicio", "ventanaFin"] else field.lower(), value)
    db.commit()
    db.refresh(db_pedido)
    return db_pedido


def delete_pedido(db: Session, db_pedido: models.Pedido):
    db.delete(db_pedido)
    db.commit()


# ===============================================================
# 🚚 CRUD PUNTO ENTREGA
# ===============================================================
def get_punto_entrega(db: Session, punto_id: int) -> Optional[models.PuntoEntrega]:
    return db.query(models.PuntoEntrega).filter(models.PuntoEntrega.id == punto_id).first()


def get_puntos_entrega(db: Session, skip: int = 0, limit: int = 100) -> List[models.PuntoEntrega]:
    return db.query(models.PuntoEntrega).offset(skip).limit(limit).all()


def create_punto_entrega(db: Session, punto) -> models.PuntoEntrega:
    db_obj = models.PuntoEntrega(
        pedido_id=punto.pedidoId,
        direccion=punto.direccion,
        latitud=punto.latitud,
        longitud=punto.longitud,
        estado=punto.estado,
        hora_estimada=punto.horaEstimada,
        hora_real=punto.horaReal,
        observaciones=punto.observaciones
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_punto_entrega(db: Session, db_punto: models.PuntoEntrega, punto_in) -> models.PuntoEntrega:
    for field, value in punto_in.dict().items():
        setattr(db_punto, field, value)
    db.commit()
    db.refresh(db_punto)
    return db_punto


def delete_punto_entrega(db: Session, db_punto: models.PuntoEntrega):
    db.delete(db_punto)
    db.commit()


# ===============================================================
# 🚛 CRUD RUTA ENTREGA
# ===============================================================
def get_ruta_entrega(db: Session, ruta_id: int) -> Optional[models.RutaEntrega]:
    return db.query(models.RutaEntrega).filter(models.RutaEntrega.id == ruta_id).first()


def get_rutas_entrega(db: Session, skip: int = 0, limit: int = 100) -> List[models.RutaEntrega]:
    return db.query(models.RutaEntrega).offset(skip).limit(limit).all()


def create_ruta_entrega(db: Session, ruta) -> models.RutaEntrega:
    db_obj = models.RutaEntrega(
        nombre=ruta.nombre,
        conductor=ruta.conductor,
        vehiculo=ruta.vehiculo,
        capacidad_volumen=ruta.capacidadVolumen,
        capacidad_peso=ruta.capacidadPeso,
        temperatura_controlada=ruta.temperaturaControlada,
        fecha_ruta=ruta.fechaRuta,
        hora_inicio=ruta.horaInicio,
        estado=ruta.estado,
        distancia_total=ruta.distanciaTotal,
        tiempo_estimado=ruta.tiempoEstimado,
        fecha_creacion=datetime.now()
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_ruta_entrega(db: Session, db_ruta: models.RutaEntrega, ruta_in) -> models.RutaEntrega:
    for field, value in ruta_in.dict().items():
        setattr(db_ruta, field, value)
    db.commit()
    db.refresh(db_ruta)
    return db_ruta


def delete_ruta_entrega(db: Session, db_ruta: models.RutaEntrega):
    db.delete(db_ruta)
    db.commit()
