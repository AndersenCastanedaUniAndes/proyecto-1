from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, func
from app.models.databases import Base  


class Venta(Base):
    __tablename__ = 'ventas'

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=False, server_default=func.now())
    vendedor = Column(String(200), nullable=False)
    vendedor_id = Column(Integer, nullable=False)
    producto = Column(String(250), nullable=False)
    producto_id = Column(Integer, nullable=False)
    cantidad = Column(Integer, nullable=False)
    valor_unitario = Column(Numeric(12, 2), nullable=False)
    valor_total = Column(Numeric(14, 2), nullable=False)
    cliente = Column(String(250), nullable=False)
    comision = Column(Numeric(10, 2), nullable=False)

    def __repr__(self):
        return (
            f"<Venta(id={self.id}, fecha={self.fecha}, vendedor='{self.vendedor}', "
            f"producto='{self.producto}', cantidad={self.cantidad}, valor_total={self.valor_total})>"
        )
