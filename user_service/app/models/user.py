from pydantic import BaseModel,Field
from typing import Optional,List
from datetime import datetime, date

class UserBase(BaseModel):
    nombre_usuario: str
    email: str
    rol: str
    estado: Optional[bool] = True
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

# Modelo de respuesta (sin contraseña)
class User(UserBase):
    usuario_id: int

    class Config:
        from_attributes = True  # necesario para usar con SQLAlchemy

# Modelo para crear usuario
class UserCreate(UserBase):
    contrasena: str

# Modelo para actualizar usuario
class UserUpdate(BaseModel):
    nombre_usuario: Optional[str] = None
    email: Optional[str] = None
    contrasena: Optional[str] = None
    rol: Optional[str] = None
    estado: Optional[bool] = None

class PutClient(BaseModel):
    client_id: int

# Modelo interno de DB (incluye contraseña)
class UserInDB(UserBase):
    usuario_id: int
    contrasena: str

    class Config:
        from_attributes = True

class PlanVentaUpdate(BaseModel):
    periodo: Optional[str] = None
    valor_ventas: Optional[float] = None
    estado: Optional[str] = None
    vendedores_ids: Optional[List[int]] = None

class ClientCreate(BaseModel):
    empresa: str
    nombre_usuario: str
    email: str
    contrasena: str
    telefono: str
    direccion: str
    ciudad: str
