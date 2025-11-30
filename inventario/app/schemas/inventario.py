from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, ConfigDict


class EstadoInventario(str, Enum):
    disponible = "disponible"
    existencias_bajas = "existencias bajas"
    agotado = "agotado"


class BodegaSchema(BaseModel):
    """Esquema de Bodega para gestión de bodegas (creación/listado)."""

    id: int | None = None
    nombre: str
    direccion: str = ""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class BodegaDetalleSchema(BaseModel):
    """Esquema de detalle de bodega asociado a un producto.

    Se usa al crear/consultar productos para conocer ubicación y stock
    por bodega.
    """

    id: int | None = None
    nombre: str
    direccion: str = ""  # se permite incluir dirección también aquí
    cantidadDisponible: int = Field(alias="cantidad_disponible")
    pasillo: str
    estante: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ProductoInventarioSchema(BaseModel):
    id: int
    nombre: str
    lote: str
    sku: str
    stockTotal: int = Field(alias="stock_total")
    stockMinimo: int = Field(alias="stock_minimo")
    status: Literal["disponible", "existencias bajas", "agotado"]
    bodegas: List[BodegaDetalleSchema]
    fechaUltimaActualizacion: datetime = Field(alias="fecha_ultima_actualizacion")
    proveedor: str
    categoria: str
    valorUnitario: float = Field(alias="valor_unitario")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class AjusteStockRequest(BaseModel):
    bodegaId: int
    delta: int


class CrearProductoRequest(BaseModel):
    nombre: str
    lote: str
    sku: str
    stockMinimo: int
    proveedor: str
    categoria: str
    valorUnitario: float
    bodegas: List[BodegaDetalleSchema]


class CrearBodegaRequest(BaseModel):
    id: int | None = None
    nombre: str
    direccion: str
