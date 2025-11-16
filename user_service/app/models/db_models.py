from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Numeric,
    ForeignKey, CheckConstraint, func
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


# ============================================================
#  Tabla de Usuarios (existente)
# ============================================================
class DBUser(Base):
    __tablename__ = 'users'

    usuario_id = Column(Integer, primary_key=True, index=True)
    nombre_usuario = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    contrasena = Column(String)
    rol = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    estado = Column(Boolean, default=True, nullable=True)

    # Relación con planes de venta
    planes_asignados = relationship("PlanVendedor", back_populates="vendedor", cascade="all, delete-orphan")


# ============================================================
#  Tabla principal: Planes de Venta
# ============================================================
class PlanVenta(Base):
    __tablename__ = 'planes_venta'

    id = Column(Integer, primary_key=True, index=True)
    periodo = Column(String(20), nullable=False)
    valor_ventas = Column(Numeric(15, 2), nullable=False)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    estado = Column(String(20), nullable=False, server_default="activo")

    vendedores_asignados = relationship("PlanVendedor", back_populates="plan", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("periodo IN ('mensual', 'trimestral', 'semestral', 'anual')", name="check_periodo_valido"),
        CheckConstraint("valor_ventas >= 0", name="check_valor_ventas_positivo"),
        CheckConstraint("estado IN ('activo', 'completado', 'pausado')", name="check_estado_valido"),
    )


# ============================================================
#  Tabla relacional: Plan ↔ Vendedores
# ============================================================
class PlanVendedor(Base):
    __tablename__ = 'plan_vendedor'

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("planes_venta.id", ondelete="CASCADE"), nullable=False)
    vendedor_id = Column(Integer, ForeignKey("users.usuario_id", ondelete="CASCADE"), nullable=False)
    fecha_asignacion = Column(DateTime(timezone=True), server_default=func.now())

    plan = relationship("PlanVenta", back_populates="vendedores_asignados")
    vendedor = relationship("DBUser", back_populates="planes_asignados")

    __table_args__ = (
        CheckConstraint("vendedor_id > 0", name="check_vendedor_valido"),
        # Si quieres evitar duplicados:
        # UniqueConstraint('plan_id', 'vendedor_id', name='unique_plan_vendedor')
    )
