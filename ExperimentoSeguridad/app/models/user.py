from pydantic import BaseModel
from typing import Optional
from datetime import datetime

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

# Modelos para autenticación y tokens
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class RevokeTokenRequest(BaseModel):
    token: str
    reason: Optional[str] = None

class BlacklistEntry(BaseModel):
    jti: str
    token_type: str
    expires_at: datetime
    revoked_at: datetime
    revoked_by: Optional[str] = None
    reason: Optional[str] = None

    class Config:
        from_attributes = True
