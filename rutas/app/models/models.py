from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum, func
from sqlalchemy.orm import relationship
from app.models.databases import Base
import enum


# Definición de Enum para estados
class EstadoPuntoEntrega(enum.Enum):
    pendiente = "pendiente"
    en_transcurso = "en-transcurso"
    entregado = "entregado"


class EstadoRutaEntrega(enum.Enum):
    planificada = "planificada"
    en_progreso = "en-progreso"
    completada = "completada"
    cancelada = "cancelada"


class Pedido(Base):
    __tablename__ = "pedido"

    id = Column(Integer, primary_key=True, index=True)
    cliente = Column(String(255), nullable=False)
    direccion = Column(String(255), nullable=False)
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)
    volumen = Column(Float, nullable=False)  # m³
    peso = Column(Float, nullable=False)  # kg
    ventana_inicio = Column(String(5), nullable=False)  # HH:MM
    ventana_fin = Column(String(5), nullable=False)  # HH:MM
    productos = Column(String, nullable=False)  # Guardar como texto (lista serializada o JSON)
    valor = Column(Float, nullable=False)
    seleccionado = Column(Boolean, default=False)
    fecha_creacion = Column(DateTime, server_default=func.now())

    puntos_entrega = relationship("PuntoEntrega", back_populates="pedido")


class PuntoEntrega(Base):
    __tablename__ = "punto_entrega"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedido.id"), nullable=False)
    ruta_id = Column(Integer, ForeignKey("ruta_entrega.id"), nullable=True)  
    direccion = Column(String(255), nullable=False)
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)
    estado = Column(Enum(EstadoPuntoEntrega), nullable=False, default=EstadoPuntoEntrega.pendiente)
    hora_estimada = Column(String(5), nullable=False)
    hora_real = Column(String(5))
    observaciones = Column(String(500))

    pedido = relationship("Pedido", back_populates="puntos_entrega")
    ruta = relationship("RutaEntrega", back_populates="puntos_entrega")



class RutaEntrega(Base):
    __tablename__ = "ruta_entrega"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    conductor = Column(String(255), nullable=False)
    vehiculo = Column(String(100), nullable=False)
    capacidad_volumen = Column(Float, nullable=False)
    capacidad_peso = Column(Float, nullable=False)
    temperatura_controlada = Column(Boolean, default=False)
    fecha_ruta = Column(String(10), nullable=False)  # YYYY-MM-DD
    hora_inicio = Column(String(5), nullable=False)
    estado = Column(Enum(EstadoRutaEntrega), nullable=False, default=EstadoRutaEntrega.planificada)
    fecha_creacion = Column(DateTime, server_default=func.now())
    distancia_total = Column(Float, nullable=False)  # km
    tiempo_estimado = Column(Float, nullable=False)  # minutos

    puntos_entrega = relationship("PuntoEntrega", back_populates="ruta")
