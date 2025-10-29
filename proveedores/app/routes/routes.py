from fastapi import UploadFile, File,APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

from ..services import crud
from ..models.proveedor import ProveedorBase, ProveedorCreate, ProveedorUpdate, ProveedorOut
from ..models.databases import get_db
from ..utils.auth import get_current_user

from ..services import crud
from ..models.databases import get_db
from ..models.proveedor import ProveedorCreate,ProveedorUpdate,ProveedorOut

router = APIRouter()


@router.get("/", response_model=List[ProveedorOut])
def get_proveedores(skip: int = 0, limit: int = 100, db: Session = Depends(get_db) ):
    return  crud.get_proveedores(db, skip=skip, limit=limit)


@router.post("/", response_model=ProveedorOut, status_code=201)
def create_proveedor(proveedor: ProveedorCreate, db: Session = Depends(get_db)):

    # asignar fechaCreacion si no viene
    if not hasattr(proveedor, 'fechaCreacion'):
        proveedor.fechaCreacion = __import__('datetime').datetime.utcnow().strftime('%Y-%m-%d')
    return crud.create_proveedor(db, proveedor)

@router.get("/{proveedor_id}", response_model=ProveedorOut)
def get_proveedor(proveedor_id: int, db: Session = Depends(get_db)):
    db_prov = crud.get_proveedor(db, proveedor_id)
    if not db_prov:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return db_prov

@router.put("/{proveedor_id}", response_model=ProveedorOut)
def update_proveedor(proveedor_id: int, proveedor_in: ProveedorUpdate, db: Session = Depends(get_db)):
    db_prov = crud.get_proveedor(db, proveedor_id)
    if not db_prov:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return crud.update_proveedor(db, db_prov, proveedor_in)

@router.delete("/{proveedor_id}", status_code=204)
def delete_proveedor(proveedor_id: int, db: Session = Depends(get_db)):
    db_prov = crud.get_proveedor(db, proveedor_id)
    if not db_prov:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    crud.delete_proveedor(db, db_prov)
    return None

