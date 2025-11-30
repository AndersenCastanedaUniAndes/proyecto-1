from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from ..application.commands import AjustarStockCommand, CrearProductoCommand, CrearBodegaCommand
from ..application.handlers import (
    handle_ajustar_stock,
    handle_crear_producto,
    handle_listar_productos,
    handle_obtener_producto,
    handle_listar_bodegas,
    handle_obtener_bodega,
    handle_crear_bodega,
)
from ..application.queries import ListarProductosQuery, ObtenerProductoQuery, ListarBodegasQuery, ObtenerBodegaQuery
from ..domain.repositories import UnitOfWork
from ..schemas.inventario import (
    AjusteStockRequest,
    CrearProductoRequest,
    BodegaSchema,
    BodegaDetalleSchema,
    ProductoInventarioSchema,
    CrearBodegaRequest,
)


def get_uow() -> UnitOfWork:
    # Dependency injected in app.__init__ at startup
    from ..container import uow

    return uow


router = APIRouter(prefix="/inventario", tags=["inventario"])


@router.get("/productos", response_model=list[ProductoInventarioSchema])
def listar_productos(q: str | None = Query(default=None), uow: UnitOfWork = Depends(get_uow)):
    query = ListarProductosQuery(q=q)
    productos = handle_listar_productos(uow, query)
    # Pydantic will use aliases for camelCase
    return [
        ProductoInventarioSchema(
            id=p.id,
            nombre=p.nombre,
            lote=p.lote,
            sku=p.sku,
            stock_total=p.stock_total,
            stock_minimo=p.stock_minimo,
            status=p.status.value,
            bodegas=[BodegaDetalleSchema.model_validate(b) for b in p.bodegas],
            fecha_ultima_actualizacion=p.fecha_ultima_actualizacion,
            proveedor=p.proveedor,
            categoria=p.categoria,
            valor_unitario=p.valor_unitario,
        )
        for p in productos
    ]


@router.get("/productos/{producto_id}", response_model=ProductoInventarioSchema)
def obtener_producto(producto_id: int, uow: UnitOfWork = Depends(get_uow)):
    query = ObtenerProductoQuery(producto_id=producto_id)
    p = handle_obtener_producto(uow, query)
    if not p:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return ProductoInventarioSchema(
        id=p.id,
        nombre=p.nombre,
        lote=p.lote,
        sku=p.sku,
        stock_total=p.stock_total,
        stock_minimo=p.stock_minimo,
        status=p.status.value,
        bodegas=[BodegaDetalleSchema.model_validate(b) for b in p.bodegas],
        fecha_ultima_actualizacion=p.fecha_ultima_actualizacion,
        proveedor=p.proveedor,
        categoria=p.categoria,
        valor_unitario=p.valor_unitario,
    )


@router.post("/productos/{producto_id}/ajustar", response_model=ProductoInventarioSchema)
def ajustar_stock(producto_id: int, body: AjusteStockRequest, uow: UnitOfWork = Depends(get_uow)):
    try:
        updated = handle_ajustar_stock(
            uow,
            AjustarStockCommand(
                producto_id=producto_id, bodega_id=body.bodegaId, delta=body.delta
            ),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return ProductoInventarioSchema(
        id=updated.id,
        nombre=updated.nombre,
        lote=updated.lote,
        sku=updated.sku,
        stock_total=updated.stock_total,
        stock_minimo=updated.stock_minimo,
        status=updated.status.value,
        bodegas=updated.bodegas,
        fecha_ultima_actualizacion=updated.fecha_ultima_actualizacion,
        proveedor=updated.proveedor,
        categoria=updated.categoria,
        valor_unitario=updated.valor_unitario,
    )


@router.post("/productos", response_model=ProductoInventarioSchema, status_code=201)
def crear_producto(body: CrearProductoRequest, uow: UnitOfWork = Depends(get_uow)):
    if body.stockMinimo < 0:
        raise HTTPException(status_code=400, detail="Stock mínimo no puede ser negativo")

    for b in body.bodegas:
        if b.cantidadDisponible < 0:
            raise HTTPException(status_code=400, detail="Cantidad disponible en bodega no puede ser negativa")

    created = handle_crear_producto(
        uow,
        CrearProductoCommand(
            nombre=body.nombre,
            lote=body.lote,
            sku=body.sku,
            stock_minimo=body.stockMinimo,
            proveedor=body.proveedor,
            categoria=body.categoria,
            valor_unitario=body.valorUnitario,
            bodegas=[b.model_dump(by_alias=True) for b in body.bodegas],
        ),
    )

    return ProductoInventarioSchema(
        id=created.id,
        nombre=created.nombre,
        lote=created.lote,
        sku=created.sku,
        stock_total=created.stock_total,
        stock_minimo=created.stock_minimo,
        status=created.status.value,
        bodegas=created.bodegas,
        fecha_ultima_actualizacion=created.fecha_ultima_actualizacion,
        proveedor=created.proveedor,
        categoria=created.categoria,
        valor_unitario=created.valor_unitario,
    )


@router.get("/bodegas", response_model=list[BodegaSchema])
def listar_bodegas(uow: UnitOfWork = Depends(get_uow)):
    bodegas = handle_listar_bodegas(uow, ListarBodegasQuery())
    return [BodegaSchema.model_validate(b) for b in bodegas]


@router.get("/bodegas/{bodega_id}", response_model=BodegaSchema)
def obtener_bodega(bodega_id: int, uow: UnitOfWork = Depends(get_uow)):
    bodega = handle_obtener_bodega(uow, ObtenerBodegaQuery(bodega_id=bodega_id))
    if not bodega:
        raise HTTPException(status_code=404, detail="Bodega no encontrada")
    return BodegaSchema.model_validate(bodega)


@router.post("/bodegas", response_model=BodegaSchema, status_code=201)
def crear_bodega(body: CrearBodegaRequest, uow: UnitOfWork = Depends(get_uow)):
    created = handle_crear_bodega(
        uow,
        CrearBodegaCommand(
            id=body.id,
            nombre=body.nombre,
            direccion=body.direccion,
        ),
    )
    return BodegaSchema.model_validate(created)

