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
    id: int
    nombre: str
    cantidad_disponible: int
    pasillo: str
    estante: str


@dataclass
class ProductoInventario:
    id: int | None
    nombre: str
    lote: str
    sku: str
    stock_total: int
    stock_minimo: int
    bodegas: List[Bodega] = field(default_factory=list)
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
        # Update stock in a specific warehouse and recompute totals
        found = False
        for b in self.bodegas:
            if b.id == bodega_id:
                nueva = b.cantidad_disponible + delta
                if nueva < 0:
                    raise ValueError("Stock en bodega no puede ser negativo")
                b.cantidad_disponible = nueva
                found = True
                break
        if not found:
            raise ValueError("Bodega no encontrada para el producto")

        self.stock_total = sum(b.cantidad_disponible for b in self.bodegas)
        self.fecha_ultima_actualizacion = datetime.utcnow()
