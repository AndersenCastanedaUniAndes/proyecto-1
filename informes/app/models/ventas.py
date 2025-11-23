from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date, datetime


class ProductoVenta(BaseModel):
    producto: str
    producto_id: int
    cantidad: int
    valor_unitario: float


class VentaBase(BaseModel):
    fecha: Optional[date] = Field(default_factory=date.today)
    vendedor: str
    vendedor_id: int
    productos: list[ProductoVenta]
    cliente: str
    comision: float

    @field_validator("vendedor", "cliente")
    def not_empty(cls, v):
        if isinstance(v, str) and not v.strip():
            raise ValueError("campo obligatorio")
        return v

    @field_validator("productos")
    def productos_not_invalid(cls, v):
        if not isinstance(v, list):
            if not v:
                raise ValueError("La lista de productos no puede estar vacía")

        for item in v:
            if isinstance(item.producto, str) and not item.producto.strip():
                raise ValueError("El nombre del producto no puede estar vacío")
            if item.producto_id is None or item.producto_id <= 0:
                raise ValueError("El ID del producto debe ser un entero positivo")
            if item.cantidad <= 0:
                raise ValueError("El valor debe ser positivo")
            if item.valor_unitario <= 0:
                raise ValueError("El valor debe ser positivo") 
        return v

    @field_validator("comision")
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
