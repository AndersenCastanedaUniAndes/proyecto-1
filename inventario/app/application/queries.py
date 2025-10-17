from dataclasses import dataclass
from typing import Optional


@dataclass
class ListarProductosQuery:
    q: Optional[str] = None


@dataclass
class ObtenerProductoQuery:
    producto_id: int
