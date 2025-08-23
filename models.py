from pydantic import BaseModel
from datetime import datetime

class PedidoCreate(BaseModel):
    cliente: str

class LineaCreate(BaseModel):
    producto: str
    cantidad: int

class PedidoResponse(BaseModel):
    id: int
    cliente: str
    fecha: datetime
    total_items: int = 0
