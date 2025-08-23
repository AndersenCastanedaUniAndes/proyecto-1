from datetime import datetime

from actions import PEDIDO_CREADO, PEDIDO_ELIMINADO, LINEA_AGREGADA
from db import execute, fetchrow
from events import publish_event

async def crear_pedido0(cliente: str):
    result = await execute(
        "INSERT INTO pedidos (cliente, fecha) VALUES ($1, $2) RETURNING id",
        cliente, datetime.now()
    )

    print(f"{PEDIDO_CREADO}: {result}")

    pedido_id = int(result.split()[-1])  # asyncpg devuelve "INSERT 0 <id>"

    await publish_event(PEDIDO_CREADO, {
        "pedido_id": pedido_id,
        "cliente": cliente,
        "fecha": str(datetime.now())
    })

    return pedido_id


async def crear_pedido(cliente: str):
    now = datetime.now()
    row = await fetchrow(
        """
        INSERT INTO pedidos (cliente, fecha)
        VALUES ($1, $2)
        RETURNING id, cliente, fecha
        """,
        cliente, now
    )

    pedido = {
        "id": row["id"],
        "cliente": row["cliente"],
        "fecha": row["fecha"],
        "total_items": 0
    }

    await publish_event(PEDIDO_CREADO, {
        "pedido_id": pedido["id"],
        "cliente": pedido["cliente"],
        "fecha": pedido["fecha"].isoformat()
    })

    return pedido


async def agregar_linea(pedido_id: int, producto: str, cantidad: int):
    await fetchrow(
        "INSERT INTO lineas_pedido (pedido_id, producto, cantidad) VALUES ($1, $2, $3)",
        pedido_id, producto, cantidad
    )

    await publish_event(LINEA_AGREGADA, {
        "pedido_id": pedido_id,
        "producto": producto,
        "cantidad": cantidad
    })


async def eliminar_pedido(pedido_id: int):
    result = await fetchrow(
        "DELETE FROM pedidos WHERE id=$1 RETURNING id, cliente, fecha",
        pedido_id
    )

    await publish_event(PEDIDO_ELIMINADO, {
        "pedido_id": pedido_id
    })

    return dict(result) if result else None
