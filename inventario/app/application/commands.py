from dataclasses import dataclass
from typing import List


@dataclass
class AjustarStockCommand:
    producto_id: int
    bodega_id: int
    delta: int  # positive for inbound, negative for outbound


@dataclass
class CrearProductoCommand:
    nombre: str
    lote: str
    sku: str
    stock_minimo: int
    proveedor: str
    categoria: str
    valor_unitario: float
    bodegas: List[dict]
