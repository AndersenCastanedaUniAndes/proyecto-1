from db import fetch

async def listar_pedidos():
    return await fetch("SELECT * FROM pedido_resumen ORDER BY fecha DESC")

async def obtener_pedido(pedido_id: int):
    rows = await fetch("SELECT * FROM pedido_resumen WHERE pedido_id=$1", pedido_id)
    return rows[0] if rows else None

async def obtener_lineas(pedido_id: int):
    return await fetch("SELECT * FROM lineas_pedido WHERE pedido_id=$1", pedido_id)