from fastapi import UploadFile, File,APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

from ..services import crud
from ..models.producto import ProductoBase, ProductoCreate, ProductoUpdate, ProductoOut
from ..models.databases import get_db
from ..utils.auth import get_current_user

from ..services import crud
from ..models.databases import get_db
from ..models.producto import ProductoCreate

router = APIRouter()

@router.get("/paises")
def get_paises( ):
    return  crud.get_paises()

@router.get("/proveedores")
def get_proveedores( ):
    return  crud.get_proveedores()


@router.get("/uom")
def get_uom( ):
    return  crud.get_uom()

@router.get("/tipos_almacenamiento")
def get_uom( ):
    return  crud.get_tipo_almacenamiento()


@router.post("/upload_excel", status_code=201)
async def upload_productos_excel( file: UploadFile = File(...),  db: Session = Depends(get_db)):
    return await crud.get_productos_creados(file, db)

@router.get("/", response_model=List[ProductoOut])
#def list_productos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _user: dict = Depends(get_current_user)):
def list_productos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_productos(db, skip=skip, limit=limit)

@router.post("/", response_model=ProductoOut, status_code=201)
#def create_producto(producto: ProductoCreate, db: Session = Depends(get_db), _user: dict = Depends(get_current_user)):
def create_producto(producto: ProductoCreate, db: Session = Depends(get_db)):
    # validar unique serial
    existing = crud.get_producto_by_serial(db, producto.numeroSerial)
    if existing:
        raise HTTPException(status_code=400, detail="Producto con ese numeroSerial ya existe")
    # asignar fechaCreacion si no viene
    if not hasattr(producto, 'fechaCreacion'):
        producto.fechaCreacion = __import__('datetime').datetime.utcnow().strftime('%Y-%m-%d')
    return crud.create_producto(db, producto)

@router.get("/{producto_id}", response_model=ProductoOut)
#def get_producto(producto_id: int, db: Session = Depends(get_db), _user: dict = Depends(get_current_user)):
def get_producto(producto_id: int, db: Session = Depends(get_db)):
    db_prod = crud.get_producto(db, producto_id)
    if not db_prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return db_prod

@router.put("/{producto_id}", response_model=ProductoOut)
#def update_producto(producto_id: int, producto_in: ProductoUpdate, db: Session = Depends(get_db), _user: dict = Depends(get_current_user)):
def update_producto(producto_id: int, producto_in: ProductoUpdate, db: Session = Depends(get_db)):
    db_prod = crud.get_producto(db, producto_id)
    if not db_prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return crud.update_producto(db, db_prod, producto_in)

@router.delete("/{producto_id}", status_code=204)
#def delete_producto(producto_id: int, db: Session = Depends(get_db), _user: dict = Depends(get_current_user)):
def delete_producto(producto_id: int, db: Session = Depends(get_db)):
    db_prod = crud.get_producto(db, producto_id)
    if not db_prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    crud.delete_producto(db, db_prod)
    return None

