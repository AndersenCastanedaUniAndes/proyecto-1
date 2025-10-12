from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime, date


class ProductoBase(BaseModel):
    nombre: str
    lote: str
    numeroSerial: str
    proveedor: str
    precioUnidad: float
    precioTotal: float
    paisOrigen: str
    uom: str
    cantidad: int
    tipoAlmacenamiento: str
    temperaturaMin: Optional[float] = None
    temperaturaMax: Optional[float] = None
    # Campo opcional, pero si no se envía se usa la fecha actual
    fechaCreacion: Optional[datetime] = Field(default_factory=datetime.utcnow)

    @field_validator("nombre", "lote", "numeroSerial", "proveedor", "paisOrigen", "uom", "tipoAlmacenamiento")
    def not_empty(cls, v):
        if isinstance(v, str) and not v.strip():
            raise ValueError("campo obligatorio")
        return v


class ProductoCreate(ProductoBase):
    pass


class ProductoUpdate(ProductoBase):
    pass


class ProductoOut(ProductoBase):
    id: int
    fechaCreacion: datetime

    class Config:
        orm_mode = True


# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
