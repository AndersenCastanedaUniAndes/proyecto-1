from datetime import datetime
import logging

from actions import INVENTARIO_CREADO, INVENTARIO_ELIMINADO, LINEA_AGREGADA
from db import fetchrow
from events import publish_event

log = logging.getLogger(__name__)


async def crear_inventario(cliente: str):
    if not cliente or not cliente.strip():
        raise ValueError("cliente no puede estar vacío")

    now = datetime.now()
    row = await fetchrow(
        """
        INSERT INTO inventario (cliente, fecha_caducidad)
        VALUES ($1, $2)
        RETURNING id, cliente, fecha_caducidad
        """,
        cliente.strip(), now
    )

    inventario = {
        "id": row["id"],
        "cliente": row["cliente"],
        "fecha_caducidad": row["fecha_caducidad"],
        "total_items": 0
    }

    try:
        await publish_event(INVENTARIO_CREADO, {
            "inventario_id": inventario["id"],
            "cliente": inventario["cliente"],
            "fecha_caducidad": inventario["fecha_caducidad"].isoformat()
        })
    except Exception as e:
        log.exception(f"Error publicando evento INVENTARIO_CREADO: {e}")

    return inventario


async def agregar_linea(inventario_id: int, producto: str, cantidad: int):
    if cantidad <= 0:
        raise ValueError("cantidad debe ser > 0")
    if not producto or not producto.strip():
        raise ValueError("producto no puede estar vacío")

    await fetchrow(
        "INSERT INTO lineas_inventario (inventario_id, producto, cantidad) VALUES ($1, $2, $3)",
        inventario_id, producto.strip(), cantidad
    )

    try:
        await publish_event(LINEA_AGREGADA, {
            "inventario_id": inventario_id,
            "producto": producto.strip(),
            "cantidad": cantidad
        })
    except Exception:
        log.exception("Error publicando evento LINEA_AGREGADA")


async def eliminar_inventario(inventario_id: int):
    result = await fetchrow(
        "DELETE FROM inventario WHERE id=$1 RETURNING id, cliente, fecha_caducidad",
        inventario_id
    )
    try:
        await publish_event(INVENTARIO_ELIMINADO, {
            "inventario_id": inventario_id
        })
    except Exception:
        log.exception("Error publicando evento INVENTARIO_ELIMINADO")
    return dict(result) if result else None
