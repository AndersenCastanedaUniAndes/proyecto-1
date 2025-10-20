from __future__ import annotations

from datetime import datetime
from typing import List

from ..domain.models import Bodega, ProductoInventario
from ..domain.repositories import UnitOfWork
from .commands import AjustarStockCommand, CrearProductoCommand
from .queries import ListarProductosQuery, ObtenerProductoQuery


def handle_listar_productos(uow: UnitOfWork, query: ListarProductosQuery) -> List[ProductoInventario]:
    with uow:
        return uow.productos.list(q=query.q)


def handle_obtener_producto(uow: UnitOfWork, query: ObtenerProductoQuery) -> ProductoInventario | None:
    with uow:
        return uow.productos.get(query.producto_id)


def handle_ajustar_stock(uow: UnitOfWork, cmd: AjustarStockCommand) -> ProductoInventario:
    with uow:
        producto = uow.productos.get(cmd.producto_id)

        if not producto:
            raise ValueError("Producto no encontrado")

        producto.ajustar_stock_bodega(cmd.bodega_id, cmd.delta)
        uow.productos.save(producto)
        uow.commit()

        return producto


def handle_crear_producto(uow: UnitOfWork, cmd: CrearProductoCommand) -> ProductoInventario:
    with uow:
        bodegas = [
            Bodega(
                id=b.get("id"),
                nombre=b["nombre"],
                cantidad_disponible=b.get("cantidad_disponible", 0),
                pasillo=b.get("pasillo", ""),
                estante=b.get("estante", ""),
            )
            for b in cmd.bodegas
        ]

        stock_total = sum(b.cantidad_disponible for b in bodegas)

        producto = ProductoInventario(
            id=None,
            nombre=cmd.nombre,
            lote=cmd.lote,
            sku=cmd.sku,
            stock_total=stock_total,
            stock_minimo=cmd.stock_minimo,
            bodegas=bodegas,
            fecha_ultima_actualizacion=datetime.utcnow(),
            proveedor=cmd.proveedor,
            categoria=cmd.categoria,
            valor_unitario=cmd.valor_unitario,
        )

        if getattr(uow.productos, "_items", None) is not None and producto.id is None:
            next_id = max((p.id for p in uow.productos.list()), default=0) + 1
            producto.id = next_id
        uow.productos.save(producto)
        uow.commit()

        return producto
