from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime, date


class ProveedorBase(BaseModel):
    nombre: str
    correoElectronico: str
    estado: str
    fechaCreacion: Optional[datetime] = Field(default_factory=datetime.utcnow)

    @field_validator("nombre", "correoElectronico", "estado")
    def not_empty(cls, v):
        if isinstance(v, str) and not v.strip():
            raise ValueError("campo obligatorio")
        return v


class ProveedorCreate(ProveedorBase):
    pass


class ProveedorUpdate(ProveedorBase):
    pass


class ProveedorOut(ProveedorBase):
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
