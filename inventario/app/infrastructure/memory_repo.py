from __future__ import annotations

from typing import Dict, List, Optional

from ..domain.models import ProductoInventario
from ..domain.repositories import ProductoInventarioRepository, UnitOfWork


class InMemoryProductoRepo(ProductoInventarioRepository):
    def __init__(self, items: Optional[List[ProductoInventario]] = None) -> None:
        self._items: Dict[int, ProductoInventario] = {p.id: p for p in (items or [])}

    def list(self, q: Optional[str] = None) -> List[ProductoInventario]:
        items = list(self._items.values())

        if q:
            q_lower = q.lower()

            items = [
                p
                for p in items
                if q_lower in p.nombre.lower()
                or q_lower in p.sku.lower()
                or q_lower in p.lote.lower()
                or q_lower in p.proveedor.lower()
            ]

        return sorted(items, key=lambda p: p.id)

    def get(self, producto_id: int) -> Optional[ProductoInventario]:
        return self._items.get(producto_id)

    def save(self, producto: ProductoInventario) -> None:
        if producto.id is None:
            next_id = max(self._items.keys(), default=0) + 1
            producto.id = next_id

        self._items[producto.id] = producto


class InMemoryUnitOfWork(UnitOfWork):
    def __init__(self, repo: InMemoryProductoRepo) -> None:
        self.productos = repo
        self.committed = False

    def __enter__(self) -> "InMemoryUnitOfWork":
        self.committed = False
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if exc:
            self.rollback()
        else:
            self.commit()

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.committed = False
