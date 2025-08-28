import asyncio
import json
import os
import logging
import redis.asyncio as redis
from datetime import datetime

from actions import INVENTARIO_CREADO, LINEA_AGREGADA, INVENTARIO_ELIMINADO
from db import execute, init_db

async def inventario_creado(event):
    p = event["payload"]
    fecha_caducidad = datetime.fromisoformat(p["fecha_caducidad"])
    await execute(
        "INSERT INTO inventario_resumen (inventario_id, cliente, total_items, fecha_caducidad) VALUES ($1, $2, $3, $4)",
        int(p["inventario_id"]), p["cliente"], 0, fecha_caducidad
    )


async def linea_agregada(event):
    p = event["payload"]
    await execute(
        "UPDATE inventario_resumen SET total_items = total_items + $1 WHERE inventario_id=$2",
        int(p["cantidad"]), int(p["inventario_id"])
    )


async def inventario_eliminado(event):
    p = event["payload"]
    await execute(
        "DELETE FROM inventario_resumen WHERE inventario_id=$1",
        int(p["inventario_id"])
    )


async def caso_default(event):
    return f"Opción {event['type']} no reconocida"


switch = {
    INVENTARIO_CREADO: inventario_creado,
    LINEA_AGREGADA: linea_agregada,
    INVENTARIO_ELIMINADO: inventario_eliminado
}

async def process_event(event):
    logging.getLogger(__name__).info(f"Procesando evento: {event}")
    option = event["type"]
    await switch.get(option, caso_default)(event)


async def main():
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
    await init_db()

    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    logging.getLogger(__name__).info(f"Suscribiéndose a Redis en {redis_url}")
    redis_client = redis.from_url(redis_url, decode_responses=True)
    pubsub = redis_client.pubsub()
    await pubsub.subscribe("events")

    async for msg in pubsub.listen():
        if msg["type"] == "message":
            event = json.loads(msg["data"])
            await process_event(event)

if __name__ == "__main__":
    asyncio.run(main())
