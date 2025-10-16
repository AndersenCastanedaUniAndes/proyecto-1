from sqlalchemy import Column, Float, Integer, String, Date, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Producto(Base):
    __tablename__ = 'productos'

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    lote = Column(String(100), nullable=False)
    numeroSerial = Column(String(200), nullable=False, unique=True)
    proveedor = Column(String(255), nullable=False)
    precioUnidad = Column(Float, nullable=False)
    precioTotal = Column(Float, nullable=False)
    paisOrigen = Column(String(100), nullable=False)
    uom = Column(String(50), nullable=False)
    cantidad = Column(Integer, nullable=False)
    tipoAlmacenamiento = Column(String(50), nullable=False)
    temperaturaMin = Column(Float, nullable=True)
    temperaturaMax = Column(Float, nullable=True)
    fechaCreacion = Column(Date, nullable=False, server_default=func.now())
    #fechaCreacion = Column(Date, nullable=False, default=func.now())