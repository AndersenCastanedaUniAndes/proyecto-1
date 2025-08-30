import asyncio, logging, json, os
import redis.asyncio as redis
from datetime import datetime
from redis.exceptions import ResponseError

import db
from db import init_db #, execute, fetchrow, fetchval
from actions import ITEM_UPSERTED, ITEM_ADJUSTED, ITEM_RESERVED
from unit_of_work import UnitOfWork

STREAM_KEY    = os.getenv("EVENT_STREAM", "events-stream")
GROUP         = os.getenv("EVENT_GROUP", "projector")
CONSUMER      = os.getenv("CONSUMER_NAME", f"c-{os.getpid()}")
CLAIM_IDLE_MS = int(os.getenv("CLAIM_IDLE_MS", "60000"))  # reclamar mensajes inactivos > 60s
DLQ_STREAM   = os.getenv("DLQ_STREAM", "events-dlq")
MAX_RETRIES  = int(os.getenv("MAX_RETRIES", "5"))
RETRY_TTL_S  = int(os.getenv("RETRY_TTL_S", "86400"))  # contador de reintentos dura 1 día


async def upsert_projection_from_db(conn, key: dict):
    row = await conn.fetchrow("""
      SELECT tenant_id, warehouse_id, location_id, product_id, lot_number, serial_number,
             qty_on_hand, qty_reserved, storage_class, expiry_date, quality_status, updated_at
      FROM inventory_item
      WHERE tenant_id=$1 AND warehouse_id=$2 AND location_id=$3 AND product_id=$4
        AND lot_number=$5 AND serial_number=$6
    """, key["tenant_id"], key["warehouse_id"], key["location_id"], key["product_id"], key["lot_number"], key["serial_number"])

    if not row:
        await conn.execute("""
          DELETE FROM inventory_search
          WHERE tenant_id=$1 AND warehouse_id=$2 AND location_id=$3 AND product_id=$4 AND lot_number=$5 AND serial_number=$6
        """, key["tenant_id"], key["warehouse_id"], key["location_id"], key["product_id"], key["lot_number"], key["serial_number"])
        return

    qty_available = int(row["qty_on_hand"]) - int(row["qty_reserved"])
    await conn.execute("""
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


async def handle_item_upserted(conn, event: dict):
    p = event["payload"]
    key = {k: (p.get(k) or "") for k in ["tenant_id","warehouse_id","location_id","product_id","lot_number","serial_number"]}
    await upsert_projection_from_db(conn, key)


async def handle_item_adjusted(conn, event: dict):
    p = event["payload"]
    key = {k: (p.get(k) or "") for k in ["tenant_id","warehouse_id","location_id","product_id","lot_number","serial_number"]}
    await upsert_projection_from_db(conn, key)


async def handle_item_reserved(conn, event: dict):
    p = event["payload"]
    key = {k: (p.get(k) or "") for k in ["tenant_id","warehouse_id","location_id","product_id","lot_number","serial_number"]}
    await upsert_projection_from_db(conn, key)


switch = {
    ITEM_UPSERTED: handle_item_upserted,
    ITEM_ADJUSTED: handle_item_adjusted,
    ITEM_RESERVED: handle_item_reserved,
}


#region Idempotencia (usa processed_events)
async def already_processed(conn, event_id: str) -> bool:
    if not event_id:
        return False
    exists = await conn.fetchval("SELECT 1 FROM processed_events WHERE event_id=$1", event_id)
    return bool(exists)


async def mark_processed(conn, event_id: str):
    if event_id:
        await conn.execute("INSERT INTO processed_events(event_id) VALUES($1) ON CONFLICT DO NOTHING", event_id)
#endregion


async def process_event(event: dict):
    async with UnitOfWork(db.pool) as conn:
        logging.getLogger(__name__).info(f"Procesando evento: {event.get('type')}")
        ev_id = event.get("id")
        if await already_processed(conn, ev_id):
            return

        handler = switch.get(event["type"])
        if handler:
            await handler(conn, event)

        await mark_processed(conn, ev_id)


# --------- Bucle del consumidor (XREADGROUP + XAUTOCLAIM) ---------
async def ensure_group(r):
    try:
        await r.xgroup_create(STREAM_KEY, GROUP, id="$", mkstream=True)
    except ResponseError as e:
        if "BUSYGROUP" not in str(e):
            raise


def _to_event(fields: dict) -> dict:
    # Campos llegan como strings; payload es JSON string
    return {
        "id"      : fields.get("id"),
        "type"    : fields.get("type"),
        "payload" : json.loads(fields.get("payload", "{}"))
    }


async def main():
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
    await init_db()

    url = os.getenv("REDIS_URL", "redis://localhost:6379")
    r = redis.from_url(url, decode_responses=True)
    await ensure_group(r)

    log = logging.getLogger(__name__)
    log.info(f"Consumidor listo: stream={STREAM_KEY} group={GROUP} consumer={CONSUMER} idle={CLAIM_IDLE_MS}ms")

    backoff = 1
    while True:
        try:
            # 1) Leer NUEVOS mensajes
            resp = await r.xreadgroup(GROUP, CONSUMER, streams={STREAM_KEY: ">"}, count=128, block=5000)
            if resp:
                _, entries = resp[0]
                for msg_id, fields in entries:
                    try:
                        event = _to_event(fields)
                        await process_event(event)
                        await r.xack(STREAM_KEY, GROUP, msg_id)
                    except Exception as e:
                        log.exception(f"Error procesando {msg_id}: {e}")

                        # contador de reintentos por mensaje
                        retry_key = f"retry:{STREAM_KEY}:{GROUP}:{msg_id}"
                        try:
                            count = int(await r.incr(retry_key))
                            await r.expire(retry_key, RETRY_TTL_S)
                        except Exception:
                            count = MAX_RETRIES + 1  # si falla redis, evita loop infinito

                        if count > MAX_RETRIES:
                            # Mover a DLQ y ACK para no ciclar
                            try:
                                await r.xadd(DLQ_STREAM, {
                                    "orig_id": msg_id,
                                    "type": fields.get("type", ""),
                                    "payload": fields.get("payload", ""),
                                    "error": str(e)[:500]
                                })
                            finally:
                                await r.xack(STREAM_KEY, GROUP, msg_id)

            # 2) Reclamar PENDIENTES inactivos (por si un consumer murió)
            next_id = "0-0"
            while True:
                next_id, claimed, _ = await r.xautoclaim(
                    STREAM_KEY, GROUP, CONSUMER, min_idle_time=CLAIM_IDLE_MS, start_id=next_id, count=128
                )

                if not claimed:
                    break

                for msg_id, fields in claimed:
                    try:
                        event = _to_event(fields)
                        await process_event(event)
                        await r.xack(STREAM_KEY, GROUP, msg_id)
                    except Exception as e:
                        log.exception(f"[reclaimed] Error {msg_id}: {e}")

                        retry_key = f"retry:{STREAM_KEY}:{GROUP}:{msg_id}"
                        try:
                            count = int(await r.incr(retry_key))
                            await r.expire(retry_key, RETRY_TTL_S)
                        except Exception:
                            count = MAX_RETRIES + 1

                        if count > MAX_RETRIES:
                            try:
                                await r.xadd(DLQ_STREAM, {
                                    "orig_id" : msg_id,
                                    "type"    : fields.get("type", ""),
                                    "payload" : fields.get("payload", ""),
                                    "error"   : str(e)[:500]
                                })
                            finally:
                                await r.xack(STREAM_KEY, GROUP, msg_id)

            # éxito → resetea backoff
            backoff = 1

            # (opcional) heartbeat para monitoreo
            try:
                hb_key = f"hb:{STREAM_KEY}:{GROUP}:{CONSUMER}"
                await r.set(hb_key, int(datetime.utcnow().timestamp()), ex=30)
            except Exception:
                pass

        except Exception as e:
            log.exception(f"Loop consumer: {e}")
            await asyncio.sleep(min(backoff, 30))
            backoff = min(backoff * 2, 30)  # backoff exponencial con techo


if __name__ == "__main__":
    asyncio.run(main())
