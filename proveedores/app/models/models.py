from sqlalchemy import Column, Integer, String, Date, func
from app.models.databases import Base  # 👈 Importa el Base compartido

class Proveedor(Base):
    __tablename__ = 'proveedor'

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    correoElectronico = Column(String(100), nullable=False)
    estado = Column(String(200), nullable=False)
    fechaCreacion = Column(Date, nullable=False, server_default=func.now())
