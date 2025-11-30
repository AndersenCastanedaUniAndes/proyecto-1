from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal
from datetime import datetime
import json


# ===============================================================
# 🧱 SCHEMAS PARA PEDIDO
# ===============================================================
class PedidoBase(BaseModel):
    cliente: str
    direccion: str
    latitud: float
    longitud: float
    volumen: float
    peso: float
    ventanaInicio: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="Formato HH:MM")
    ventanaFin: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="Formato HH:MM")
    productos: List[str]
    valor: float
    seleccionado: bool = False

    @field_validator("cliente", "direccion")
    def not_empty(cls, v):
        if isinstance(v, str) and not v.strip():
            raise ValueError("campo obligatorio")
        return v


class PedidoCreate(PedidoBase):
    pass


class PedidoUpdate(PedidoBase):
    pass


class PedidoOut(BaseModel):
    id: int
    cliente: str
    direccion: str
    latitud: float
    longitud: float
    volumen: float
    peso: float
    ventanaInicio: str = Field(..., alias="ventana_inicio")
    ventanaFin: str = Field(..., alias="ventana_fin")
    productos: List[str]
    valor: float
    seleccionado: bool
    fechaCreacion: datetime = Field(..., alias="fecha_creacion")

    @field_validator("productos", mode="before")
    def parse_productos(cls, v):
        # Si viene como string JSON, conviértelo en lista real
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                # fallback por si solo vienen separados por comas
                return [p.strip() for p in v.strip("[]").split(",")]
        return v

    class Config:
        orm_mode = True
        populate_by_name = True  # permite usar alias al serializar


# ===============================================================
# 🚚 SCHEMAS PARA PUNTO ENTREGA
# ===============================================================
class PuntoEntregaBase(BaseModel):
    pedidoId: int
    direccion: str
    latitud: float
    longitud: float
    estado: Literal["pendiente", "en-transcurso", "entregado"] = "pendiente"
    horaEstimada: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    horaReal: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    observaciones: Optional[str] = None

    @field_validator("direccion")
    def not_empty(cls, v):
        if isinstance(v, str) and not v.strip():
            raise ValueError("campo obligatorio")
        return v


class PuntoEntregaCreate(PuntoEntregaBase):
    pass


class PuntoEntregaUpdate(PuntoEntregaBase):
    pass


class PuntoEntregaOut(BaseModel):
    id: int
    pedidoId: int = Field(..., alias="pedido_id")
    direccion: str
    latitud: float
    longitud: float
    estado: Literal["pendiente", "en-transcurso", "entregado"]
    horaEstimada: str = Field(..., alias="hora_estimada")
    horaReal: Optional[str] = Field(None, alias="hora_real")
    observaciones: Optional[str] = None

    @field_validator("estado", mode="before")
    def convert_enum_to_str(cls, v):
        # ✅ Convierte Enum a string si es necesario
        if hasattr(v, "value"):
            return v.value
        return v

    class Config:
        orm_mode = True
        populate_by_name = True

# ===============================================================
# 🚛 SCHEMAS PARA RUTA ENTREGA
# ===============================================================
class RutaEntregaBase(BaseModel):
    nombre: str
    conductor: str
    vehiculo: str
    capacidadVolumen: float
    capacidadPeso: float
    temperaturaControlada: bool = False
    fechaRuta: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Formato YYYY-MM-DD")
    horaInicio: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    estado: Literal["planificada", "en-progreso", "completada", "cancelada"] = "planificada"
    distanciaTotal: float
    tiempoEstimado: float

    @field_validator("nombre", "conductor", "vehiculo")
    def not_empty(cls, v):
        if isinstance(v, str) and not v.strip():
            raise ValueError("campo obligatorio")
        return v


class RutaEntregaCreate(RutaEntregaBase):
    puntosEntrega: Optional[List[PuntoEntregaCreate]] = None


class RutaEntregaUpdate(RutaEntregaBase):
    puntosEntrega: Optional[List[PuntoEntregaUpdate]] = None


class RutaEntregaOut(BaseModel):
    id: int
    nombre: str
    conductor: str
    vehiculo: str
    capacidadVolumen: float = Field(..., alias="capacidad_volumen")
    capacidadPeso: float = Field(..., alias="capacidad_peso")
    temperaturaControlada: Optional[bool] = Field(..., alias="temperatura_controlada")
    fechaRuta: str = Field(..., alias="fecha_ruta")
    horaInicio: str = Field(..., alias="hora_inicio")
    estado: Literal["planificada", "en-progreso", "completada", "cancelada"]
    fechaCreacion: Optional[datetime] = Field(None, alias="fecha_creacion")
    distanciaTotal: float = Field(..., alias="distancia_total")
    tiempoEstimado: float = Field(..., alias="tiempo_estimado")

    # Si incluyes puntos de entrega asociados:
    # puntosEntrega: Optional[List[PuntoEntregaOut]] = Field(None, alias="puntos_entrega")

    @field_validator("estado", mode="before")
    def convert_enum_to_str(cls, v):
        # Convierte Enum a string si viene desde SQLAlchemy
        if hasattr(v, "value"):
            return v.value
        return v

    class Config:
        orm_mode = True
        populate_by_name = True

    class Config:
        orm_mode = True
