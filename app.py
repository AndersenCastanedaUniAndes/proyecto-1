from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from models import PedidoCreate, LineaCreate, PedidoResponse
import commands, queries
from db import init_db
from events import init_redis


app = FastAPI()


@app.on_event("startup")
async def startup():
    await init_db()
    await init_redis()


# --- COMANDOS ---
@app.post("/pedidos", response_model=PedidoResponse)
async def crear_pedido(data: PedidoCreate):
    pedido = await commands.crear_pedido(data.cliente)
    return pedido


@app.post("/pedidos/{pedido_id}/linea")
async def agregar_linea(pedido_id: int, data: LineaCreate):
    await commands.agregar_linea(pedido_id, data.producto, data.cantidad)
    return {"status": "ok"}


@app.delete("/pedidos/{pedido_id}")
async def eliminar_pedido(pedido_id: int):
    pedido = await commands.eliminar_pedido(pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return {"status": "deleted", "pedido": pedido}


# --- QUERIES ---
@app.get("/pedidos")
async def listar_pedidos():
    pedidos = await queries.listar_pedidos()
    return [dict(p) for p in pedidos]


@app.get("/pedidos/{pedido_id}")
async def obtener_pedido(pedido_id: int):
    pedido = await queries.obtener_pedido(pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="No encontrado")

    result = dict(pedido)
    result["items"] = await queries.obtener_lineas(pedido_id)

    return result
