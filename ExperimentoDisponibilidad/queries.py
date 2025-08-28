from db import fetch

async def listar_inventario():
    return await fetch("SELECT * FROM inventario_resumen ORDER BY fecha_caducidad DESC")

async def obtener_inventario(inventario_id: int):
    rows = await fetch("SELECT * FROM inventario_resumen WHERE inventario_id=$1", inventario_id)
    return rows[0] if rows else None

async def obtener_lineas(inventario_id: int):
    return await fetch("SELECT * FROM lineas_inventario WHERE inventario_id=$1", inventario_id)