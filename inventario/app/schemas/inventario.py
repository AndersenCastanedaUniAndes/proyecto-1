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
    id: int
    nombre: str
    cantidadDisponible: int = Field(alias="cantidad_disponible")
    pasillo: str
    estante: str

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class ProductoInventarioSchema(BaseModel):
    id: int
    nombre: str
    lote: str
    sku: str
    stockTotal: int = Field(alias="stock_total")
    stockMinimo: int = Field(alias="stock_minimo")
    status: Literal["disponible", "existencias bajas", "agotado"]
    bodegas: List[BodegaSchema]
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
    bodegas: List[BodegaSchema]
