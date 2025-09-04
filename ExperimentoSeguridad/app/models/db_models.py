from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class DBUser(Base):
    __tablename__ = 'users'

    usuario_id = Column(Integer, primary_key=True, index=True)
    nombre_usuario = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    contrasena = Column(String)
    rol = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relación con refresh tokens
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")

class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'

    jti = Column(String, primary_key=True, index=True)  # JWT ID
    user_id = Column(Integer, ForeignKey('users.usuario_id'), nullable=False)
    token_hash = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)
    revoked_at = Column(DateTime, nullable=True)
    revoked_by = Column(String, nullable=True)
    reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relación con usuario
    user = relationship("DBUser", back_populates="refresh_tokens")

class TokenBlacklist(Base):
    __tablename__ = 'token_blacklist'

    jti = Column(String, primary_key=True, index=True)  # JWT ID
    token_type = Column(String, nullable=False)  # 'access' o 'refresh'
    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime, default=datetime.utcnow)
    revoked_by = Column(String, nullable=True)
    reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


