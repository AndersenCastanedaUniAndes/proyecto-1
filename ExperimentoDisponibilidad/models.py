from pydantic import BaseModel
from datetime import datetime

class InventarioCreate(BaseModel):
    cliente: str

class LineaCreate(BaseModel):
    producto: str
    cantidad: int

class InventarioResponse(BaseModel):
    id: int
    cliente: str
    fecha_caducidad: datetime
    total_items: int = 0
