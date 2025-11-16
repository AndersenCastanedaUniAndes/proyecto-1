from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.services import crud
from app.models.databases import get_db
from app.models.schemas_rutas import (
    PedidoCreate, PedidoUpdate, PedidoOut,
    PuntoEntregaCreate, PuntoEntregaUpdate, PuntoEntregaOut,
    RutaEntregaCreate, RutaEntregaUpdate, RutaEntregaOut
)

router = APIRouter()

# ===============================================================
# 📦 PEDIDOS
# ===============================================================
@router.get("/pedidos", response_model=List[PedidoOut])
def get_pedidos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_pedidos(db, skip=skip, limit=limit)


@router.post("/pedidos", response_model=PedidoOut, status_code=201)
def create_pedido(pedido: PedidoCreate, db: Session = Depends(get_db)):
    return crud.create_pedido(db, pedido)


@router.get("/pedidos/{pedido_id}", response_model=PedidoOut)
def get_pedido(pedido_id: int, db: Session = Depends(get_db)):
    db_pedido = crud.get_pedido(db, pedido_id)
    if not db_pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return db_pedido


@router.put("/pedidos/{pedido_id}", response_model=PedidoOut)
def update_pedido(pedido_id: int, pedido_in: PedidoUpdate, db: Session = Depends(get_db)):
    db_pedido = crud.get_pedido(db, pedido_id)
    if not db_pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return crud.update_pedido(db, db_pedido, pedido_in)


@router.delete("/pedidos/{pedido_id}", status_code=204)
def delete_pedido(pedido_id: int, db: Session = Depends(get_db)):
    db_pedido = crud.get_pedido(db, pedido_id)
    if not db_pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    crud.delete_pedido(db, db_pedido)
    return None


# ===============================================================
# 🚚 PUNTOS DE ENTREGA
# ===============================================================
@router.get("/puntos-entrega", response_model=List[PuntoEntregaOut])
def get_puntos_entrega(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_puntos_entrega(db, skip=skip, limit=limit)


@router.post("/puntos-entrega", response_model=PuntoEntregaOut, status_code=201)
def create_punto_entrega(punto: PuntoEntregaCreate, db: Session = Depends(get_db)):
    return crud.create_punto_entrega(db, punto)


@router.get("/puntos-entrega/{punto_id}", response_model=PuntoEntregaOut)
def get_punto_entrega(punto_id: int, db: Session = Depends(get_db)):
    db_punto = crud.get_punto_entrega(db, punto_id)
    if not db_punto:
        raise HTTPException(status_code=404, detail="Punto de entrega no encontrado")
    return db_punto


@router.put("/puntos-entrega/{punto_id}", response_model=PuntoEntregaOut)
def update_punto_entrega(punto_id: int, punto_in: PuntoEntregaUpdate, db: Session = Depends(get_db)):
    db_punto = crud.get_punto_entrega(db, punto_id)
    if not db_punto:
        raise HTTPException(status_code=404, detail="Punto de entrega no encontrado")
    return crud.update_punto_entrega(db, db_punto, punto_in)


@router.delete("/puntos-entrega/{punto_id}", status_code=204)
def delete_punto_entrega(punto_id: int, db: Session = Depends(get_db)):
    db_punto = crud.get_punto_entrega(db, punto_id)
    if not db_punto:
        raise HTTPException(status_code=404, detail="Punto de entrega no encontrado")
    crud.delete_punto_entrega(db, db_punto)
    return None


# ===============================================================
# 🚛 RUTAS DE ENTREGA
# ===============================================================
@router.get("/rutas-entrega", response_model=List[RutaEntregaOut])
def get_rutas_entrega(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_rutas_entrega(db, skip=skip, limit=limit)


@router.post("/rutas-entrega", response_model=RutaEntregaOut, status_code=201)
def create_ruta_entrega(ruta: RutaEntregaCreate, db: Session = Depends(get_db)):
    return crud.create_ruta_entrega(db, ruta)


@router.get("/rutas-entrega/{ruta_id}", response_model=RutaEntregaOut)
def get_ruta_entrega(ruta_id: int, db: Session = Depends(get_db)):
    db_ruta = crud.get_ruta_entrega(db, ruta_id)
    if not db_ruta:
        raise HTTPException(status_code=404, detail="Ruta de entrega no encontrada")
    return db_ruta


@router.put("/rutas-entrega/{ruta_id}", response_model=RutaEntregaOut)
def update_ruta_entrega(ruta_id: int, ruta_in: RutaEntregaUpdate, db: Session = Depends(get_db)):
    db_ruta = crud.get_ruta_entrega(db, ruta_id)
    if not db_ruta:
        raise HTTPException(status_code=404, detail="Ruta de entrega no encontrada")
    return crud.update_ruta_entrega(db, db_ruta, ruta_in)


@router.delete("/rutas-entrega/{ruta_id}", status_code=204)
def delete_ruta_entrega(ruta_id: int, db: Session = Depends(get_db)):
    db_ruta = crud.get_ruta_entrega(db, ruta_id)
    if not db_ruta:
        raise HTTPException(status_code=404, detail="Ruta de entrega no encontrada")
    crud.delete_ruta_entrega(db, db_ruta)
    return None
