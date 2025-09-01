from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    nombre_usuario: str
    email: str
    rol: str

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

# Modelo interno de DB (incluye contraseña)
class UserInDB(UserBase):
    usuario_id: int
    contrasena: str

    class Config:
        from_attributes = True
