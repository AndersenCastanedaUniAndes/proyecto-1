from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date, datetime


class VentaBase(BaseModel):
    fecha: Optional[date] = Field(default_factory=date.today)
    vendedor: str
    vendedor_id: int
    producto: str
    producto_id: int
    cantidad: int
    valor_unitario: float
    valor_total: Optional[float] = None
    cliente: str
    comision: float

    @field_validator("vendedor", "producto", "cliente")
    def not_empty(cls, v):
        if isinstance(v, str) and not v.strip():
            raise ValueError("campo obligatorio")
        return v

    @field_validator("cantidad", "valor_unitario", "comision")
    def positive_values(cls, v):
        if v is not None and v < 0:
            raise ValueError("El valor debe ser positivo")
        return v


class VentaCreate(VentaBase):
    """Esquema para crear una venta"""
    pass


class VentaUpdate(VentaBase):
    """Esquema para actualizar una venta"""
    id: Optional[int] = None


class VentaOut(VentaBase):
    """Esquema para devolver una venta (lectura)"""
    id: int
    fecha: date

    class Config:
        orm_mode = True
