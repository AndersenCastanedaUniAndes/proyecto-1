from fastapi import FastAPI, HTTPException, Response
from models import ItemUpsert, StockAdjust, StockReserve, ItemResponse, ItemKey
import commands, queries
from db import init_db, pool
from events import init_redis, redis_client
import logging, os


logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
app = FastAPI(title="CQRS inventario API", version="1.1.0")


@app.on_event("startup")
async def startup():
    await init_db()
    await init_redis()


@app.get("/healthz")
async def healthz(): return {"status":"ok"}


@app.get("/readyz")
async def readyz():
    try:
        async with pool.acquire() as conn:
            await conn.fetchval("select 1")
        assert redis_client is not None
        await redis_client.ping()
        return {"status":"ready"}
    except Exception:
        return Response(status_code=503, content='{"status":"not-ready"}', media_type="application/json")


# --- COMANDOS ---
@app.post("/items/upsert", response_model=ItemResponse)
async def upsert_item(data: ItemUpsert):
    payload = await commands.upsert_item(data)

    print(f"\npayload: {payload}\n")

    return ItemResponse(
        tenant_id      = payload["tenant_id"],
        warehouse_id   = payload["warehouse_id"],
        location_id    = payload["location_id"],
        product_id     = payload["product_id"],
        lot_number     = payload["lot_number"],
        serial_number  = payload["serial_number"],
        qty_on_hand    = int(payload["qty_on_hand"]),
        qty_reserved   = int(payload["qty_reserved"]),
        qty_available  = int(payload["qty_on_hand"]) - int(payload["qty_reserved"]),
        storage_class  = payload["storage_class"],
        expiry_date    = payload["expiry_date"],
        quality_status = payload["quality_status"],
        updated_at     = payload["updated_at"]
    )


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
