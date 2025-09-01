from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class DBUser(Base):
    __tablename__ = 'users'

    usuario_id = Column(Integer, primary_key=True, index=True)
    nombre_usuario = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    contrasena = Column(String)
    rol = Column(String)


