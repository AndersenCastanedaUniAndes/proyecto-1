from fastapi import FastAPI, HTTPException, Response
from models import ItemUpsert, StockAdjust, StockReserve, ItemResponse, ItemKey
import commands, queries
import db, events
from db import init_db
from events import init_redis
import logging, os


logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
app = FastAPI(title="CQRS inventario API", version="1.1.0")


@app.on_event("startup")
async def startup():
    await init_db()
    await init_redis()


@app.get("/healthz")
async def healthz():
    return {"status":"ok"}


@app.get("/readyz")
async def readyz():
    import json, asyncio
    errors = []
    try:
        async with db.pool.acquire() as conn:
            await conn.fetchval("select 1")
    except Exception as e:
        errors.append(f"db:{e}")
    try:
        if not events.redis_client:
            raise RuntimeError("redis_client=None")
        # timeout defensivo
        await asyncio.wait_for(events.redis_client.ping(), timeout=1.0)
    except Exception as e:
        errors.append(f"redis:{e}")
    if errors:
        return Response(
            status_code=503,
            content=json.dumps({"status":"not-ready","errors":errors}),
            media_type="application/json",
        )
    return {"status":"ready"}


# --- COMANDOS ---
@app.post("/items/upsert", response_model=ItemResponse)
async def upsert_item(data: ItemUpsert):
    response = await commands.upsert_item(data)
    return response


@app.post("/items/adjust")
async def adjust_stock(data: StockAdjust):
    await commands.adjust_stock(data)
    return {"status": "ok"}


@app.post("/items/reserve")
async def reserve_stock(data: StockReserve):
    await commands.reserve_stock(data)
    return {"status": "ok"}


# --- QUERIES ---
@app.get("/inventario")
async def listar_inventario():
    inventario = await queries.listar_inventario()
    return [dict(p) for p in inventario]


@app.get("/inventario/{inventario_id}")
async def obtener_inventario(inventario_id: int):
    inventario = await queries.obtener_inventario(inventario_id)
    if not inventario:
        raise HTTPException(status_code=404, detail="No encontrado")

    result = dict(inventario)
    result["items"] = await queries.obtener_lineas(inventario_id)

    return result


@app.get("/items")
async def listar_items(tenant_id: str, warehouse_id: str):
    rows = await queries.listar_items(tenant_id, warehouse_id)
    return [dict(r) for r in rows]


@app.get("/items/by-key")
async def get_item_by_key(tenant_id: str, warehouse_id: str, location_id: str, product_id: str,
                          lot_number: str = "", serial_number: str = ""):
    key = ItemKey(
        tenant_id     = tenant_id,
        warehouse_id  = warehouse_id,
        location_id   = location_id,
        product_id    = product_id,
        lot_number    = lot_number,
        serial_number = serial_number
    )

    row = await queries.obtener_item(key)
    if not row:
        raise HTTPException(status_code=404, detail="No encontrado")
    return dict(row)
