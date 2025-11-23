from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List


class EstadoInventario(str, Enum):
    disponible = "disponible"
    existencias_bajas = "existencias bajas"
    agotado = "agotado"


@dataclass
class Bodega:
    id: int | None
    nombre: str
    direccion: str = ""


@dataclass
class BodegaDetalle:
    id: int | None
    nombre: str
    direccion: str = ""
    cantidad_disponible: int = 0
    pasillo: str = ""
    estante: str = ""


@dataclass
class ProductoInventario:
    id: int | None
    nombre: str
    lote: str
    sku: str
    stock_total: int
    stock_minimo: int
    bodegas: List[BodegaDetalle] = field(default_factory=list)
    fecha_ultima_actualizacion: datetime = field(default_factory=datetime.utcnow)
    proveedor: str = ""
    categoria: str = ""
    valor_unitario: float = 0.0

    @property
    def status(self) -> EstadoInventario:
        if self.stock_total <= 0:
            return EstadoInventario.agotado
        if self.stock_total <= self.stock_minimo:
            return EstadoInventario.existencias_bajas
        return EstadoInventario.disponible

    def ajustar_stock_bodega(self, bodega_id: int, delta: int) -> None:
        found = False

        for b in self.bodegas:
            if b.id == bodega_id:
                # El ajuste de stock ahora se hace a nivel de inventario_bodega
                # Este método se mantiene para compatibilidad, pero el dominio
                # de Bodega ya no tiene campos de cantidad.
                found = True
                break

        if not found:
            raise ValueError("Bodega no encontrada para el producto")

        # El cálculo de stock_total ahora debe hacerse desde infraestructura
        # en función de inventario_bodega.
        self.fecha_ultima_actualizacion = datetime.utcnow()