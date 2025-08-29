import asyncio
import json
import os
import logging
import asyncio, json, os, logging
import redis.asyncio as redis
from datetime import datetime

from actions import ITEM_UPSERTED, ITEM_ADJUSTED, ITEM_RESERVED
from db import init_db, execute, fetchrow, fetchval


async def caso_default(event):
    return f"Opción {event['type']} no reconocida"


async def upsert_projection_from_db(key):
    row = await fetchrow("""
      SELECT tenant_id, warehouse_id, location_id, product_id, lot_number, serial_number,
             qty_on_hand, qty_reserved, storage_class, expiry_date, quality_status, updated_at
      FROM inventory_item
      WHERE tenant_id=$1 AND warehouse_id=$2 AND location_id=$3 AND product_id=$4
        AND lot_number=$5 AND serial_number=$6
    """, key["tenant_id"], key["warehouse_id"], key["location_id"], key["product_id"], key["lot_number"], key["serial_number"])
    if not row:
        # Si no existe ya en write-side, borra del read-side
        await execute("""
          DELETE FROM inventory_search
          WHERE tenant_id=$1 AND warehouse_id=$2 AND location_id=$3 AND product_id=$4 AND lot_number=$5 AND serial_number=$6
        """, key["tenant_id"], key["warehouse_id"], key["location_id"], key["product_id"], key["lot_number"], key["serial_number"])
        return

    qty_available = int(row["qty_on_hand"]) - int(row["qty_reserved"])
    await execute("""
      INSERT INTO inventory_search
        (tenant_id, warehouse_id, location_id, product_id, lot_number, serial_number,
         qty_on_hand, qty_reserved, qty_available, storage_class, expiry_date, quality_status, updated_at)
      VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13)
      ON CONFLICT (tenant_id, warehouse_id, location_id, product_id, lot_number, serial_number)
      DO UPDATE SET
        qty_on_hand=excluded.qty_on_hand,
        qty_reserved=excluded.qty_reserved,
        qty_available=excluded.qty_available,
        storage_class=excluded.storage_class,
        expiry_date=excluded.expiry_date,
        quality_status=excluded.quality_status,
        updated_at=excluded.updated_at
    """,
    row["tenant_id"], row["warehouse_id"], row["location_id"], row["product_id"], row["lot_number"], row["serial_number"],
    row["qty_on_hand"], row["qty_reserved"], qty_available, row["storage_class"], row["expiry_date"], row["quality_status"], row["updated_at"])

async def handle_item_upserted(event):
    p = event["payload"]
    key = {k: (p.get(k) or "") for k in ["tenant_id","warehouse_id","location_id","product_id","lot_number","serial_number"]}
    await upsert_projection_from_db(key)

async def handle_item_adjusted(event):
    p = event["payload"]
    key = {k: (p.get(k) or "") for k in ["tenant_id","warehouse_id","location_id","product_id","lot_number","serial_number"]}
    await upsert_projection_from_db(key)

async def handle_item_reserved(event):
    p = event["payload"]
    key = {k: (p.get(k) or "") for k in ["tenant_id","warehouse_id","location_id","product_id","lot_number","serial_number"]}
    await upsert_projection_from_db(key)

# Idempotencia (usa processed_events)
async def already_processed(event_id: str) -> bool:
    if not event_id:
        return False
    exists = await fetchval("SELECT 1 FROM processed_events WHERE event_id=$1", event_id)
    return bool(exists)

async def mark_processed(event_id: str):
    if event_id:
        await execute("INSERT INTO processed_events(event_id) VALUES($1) ON CONFLICT DO NOTHING", event_id)

# switch existente + nuevos
switch = {
    ITEM_UPSERTED: handle_item_upserted,
    ITEM_ADJUSTED: handle_item_adjusted,
    ITEM_RESERVED: handle_item_reserved,
}

async def process_event(event):
    logging.getLogger(__name__).info(f"Procesando evento: {event.get('type')}")
    ev_id = event.get("id")
    if await already_processed(ev_id):
        return
    handler = switch.get(event["type"])
    if handler:
        await handler(event)
    await mark_processed(ev_id)


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
