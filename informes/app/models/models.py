from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, func, JSON
from app.models.database import Base  


class Venta(Base):
    __tablename__ = 'ventas'

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=False, server_default=func.now())
    vendedor = Column(String(200), nullable=False)
    vendedor_id = Column(Integer, nullable=False)
    productos = Column(JSON, nullable=False)
    cliente = Column(String(250), nullable=False)
    cliente_id = Column(Integer, nullable=False)
    comision = Column(Numeric(10, 2), nullable=False)
    estado = Column(String(50), nullable=False, default="Pendiente") # Pendiente | Procesando | Enviado

    def __repr__(self):
        # self.productos a dictionary or JSON string if needed
        return (
            f"<Venta(id={self.id}, fecha={self.fecha}, vendedor='{self.vendedor}', "
            f"productos='{self.productos}', cliente='{self.cliente}', cliente_id={self.cliente_id}, comision={self.comision}, estado='{self.estado}')>"
        )


class DBVisita(Base):
    __tablename__ = 'visitas'

    id = Column(Integer, primary_key=True, index=True)
    cliente = Column(String(250), nullable=False)
    cliente_id = Column(Integer, nullable=False)
    vendedor = Column(String(200), nullable=False)
    vendedor_id = Column(Integer, nullable=False)
    fecha = Column(Date, nullable=False, server_default=func.now())
    direccion = Column(String(300), nullable=True)
    hallazgos = Column(String(500), nullable=True)
    sugerencias = Column(String(500), nullable=True)

    def __repr__(self):
        return (
            f"<Visita(id={self.id}, fecha={self.fecha}, cliente='{self.cliente}', "
            f"vendedor='{self.vendedor}')>"
        )
