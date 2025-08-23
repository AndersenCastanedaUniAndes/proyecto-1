import asyncio
import json
import redis.asyncio as redis
from datetime import datetime

from actions import PEDIDO_CREADO, LINEA_AGREGADA, PEDIDO_ELIMINADO
from db import execute, init_db

async def pedido_creado(event):
    p = event["payload"]
    fecha = datetime.fromisoformat(p["fecha"])
    await execute(
        "INSERT INTO pedido_resumen (pedido_id, cliente, total_items, fecha) VALUES ($1, $2, $3, $4)",
        int(p["pedido_id"]), p["cliente"], 0, fecha
    )


async def linea_agregada(event):
    p = event["payload"]
    await execute(
        "UPDATE pedido_resumen SET total_items = total_items + $1 WHERE pedido_id=$2",
        int(p["cantidad"]), int(p["pedido_id"])
    )


async def pedido_eliminado(event):
    p = event["payload"]
    await execute(
        "DELETE FROM pedido_resumen WHERE pedido_id=$1",
        int(p["pedido_id"])
    )


async def caso_default(event):
    return "Opción no reconocida"


switch = {
    PEDIDO_CREADO: pedido_creado,
    LINEA_AGREGADA: linea_agregada,
    PEDIDO_ELIMINADO: pedido_eliminado
}

async def process_event(event):
    print(f"Procesando evento: {event}")
    option = event["type"]
    await switch.get(option, caso_default)(event)


async def main():
    await init_db()
    redis_client = redis.from_url("redis://localhost", decode_responses=True)
    pubsub = redis_client.pubsub()
    await pubsub.subscribe("events")

    async for msg in pubsub.listen():
        if msg["type"] == "message":
            event = json.loads(msg["data"])
            await process_event(event)

if __name__ == "__main__":
    asyncio.run(main())
