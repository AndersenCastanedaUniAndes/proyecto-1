from fastapi import FastAPI, HTTPException
from models import InventarioCreate, LineaCreate, InventarioResponse
import commands, queries
from db import init_db
from events import init_redis
import logging, os


logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
app = FastAPI(title="CQRS inventario API", version="1.1.0")


@app.on_event("startup")
async def startup():
    await init_db()
    await init_redis()


# --- COMANDOS ---
@app.post("/inventario", response_model=InventarioResponse)
async def crear_inventario(data: InventarioCreate):
    try:
        inventario = await commands.crear_inventario(data.cliente)
        return inventario
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@app.post("/inventario/{inventario_id}/linea")
async def agregar_linea(inventario_id: int, data: LineaCreate):
    try:
        await commands.agregar_linea(inventario_id, data.producto, data.cantidad)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    return {"status": "ok"}


@app.delete("/inventario/{inventario_id}")
async def eliminar_inventario(inventario_id: int):
    inventario = await commands.eliminar_inventario(inventario_id)
    if not inventario:
        raise HTTPException(status_code=404, detail="Inventario no encontrado")

    return {"status": "deleted", "inventario": inventario}


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
