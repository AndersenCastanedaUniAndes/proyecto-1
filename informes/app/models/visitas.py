from pydantic import BaseModel, Field, field_validator
from typing import Optional

class VisitaBase(BaseModel):
    cliente: str
    cliente_id: int
    vendedor: str
    vendedor_id: int
    fecha: str
    hora: str
    direccion: str
    hallazgos: Optional[str] = None
    sugerencias: Optional[str] = None

class VisitaCreate(VisitaBase):
    """Esquema para crear una visita"""
    pass

