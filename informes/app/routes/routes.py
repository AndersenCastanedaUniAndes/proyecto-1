from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from ..services import crud
from ..models.databases import get_db
from ..models.ventas import VentaCreate, VentaUpdate, VentaOut

router = APIRouter()


@router.get("/", response_model=List[VentaOut])
def get_ventas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtener listado de ventas"""
    return crud.get_ventas(db, skip=skip, limit=limit)


@router.post("/", response_model=VentaOut, status_code=201)
def create_venta(venta: VentaCreate, db: Session = Depends(get_db)):
    """Crear una nueva venta"""
    if not hasattr(venta, 'fecha') or venta.fecha is None:
        venta.fecha = date.today()
    return crud.create_venta(db, venta)


@router.get("/{venta_id}", response_model=VentaOut)
def get_venta(venta_id: int, db: Session = Depends(get_db)):
    """Obtener una venta por su ID"""
    db_venta = crud.get_venta(db, venta_id)
    if not db_venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return db_venta


@router.put("/{venta_id}", response_model=VentaOut)
def update_venta(venta_id: int, venta_in: VentaUpdate, db: Session = Depends(get_db)):
    """Actualizar una venta existente"""
    db_venta = crud.get_venta(db, venta_id)
    if not db_venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return crud.update_venta(db, db_venta, venta_in)


@router.delete("/{venta_id}", status_code=204)
def delete_venta(venta_id: int, db: Session = Depends(get_db)):
    """Eliminar una venta"""
    db_venta = crud.get_venta(db, venta_id)
    if not db_venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    crud.delete_venta(db, db_venta)
    return None
