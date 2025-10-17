from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from .models import ProductoInventario


class ProductoInventarioRepository(ABC):
    @abstractmethod
    def list(self, q: Optional[str] = None) -> List[ProductoInventario]:
        raise NotImplementedError

    @abstractmethod
    def get(self, producto_id: int) -> Optional[ProductoInventario]:
        raise NotImplementedError

    @abstractmethod
    def save(self, producto: ProductoInventario) -> None:
        raise NotImplementedError


class UnitOfWork(ABC):
    productos: ProductoInventarioRepository

    @abstractmethod
    def __enter__(self) -> "UnitOfWork":
        raise NotImplementedError

    @abstractmethod
    def __exit__(self, exc_type, exc, tb) -> None:
        raise NotImplementedError

    @abstractmethod
    def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def rollback(self) -> None:
        raise NotImplementedError
