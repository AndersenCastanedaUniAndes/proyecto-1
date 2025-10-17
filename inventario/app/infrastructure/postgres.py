from __future__ import annotations

import os
from contextlib import AbstractContextManager
from dataclasses import asdict
from datetime import datetime
from typing import Callable, List, Optional

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    create_engine,
    select,
    func,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    Session,
    sessionmaker,
    joinedload,
)

from ..domain.models import Bodega as BodegaDomain
from ..domain.models import ProductoInventario as ProductoDomain
from ..domain.repositories import ProductoInventarioRepository, UnitOfWork


class Base(DeclarativeBase):
    pass


class ProductoORM(Base):
    __tablename__ = "productos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    lote: Mapped[str] = mapped_column(String(100), nullable=False)
    sku: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    stock_minimo: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    proveedor: Mapped[str] = mapped_column(String(255), default="")
    categoria: Mapped[str] = mapped_column(String(255), default="")
    valor_unitario: Mapped[float] = mapped_column(Float, default=0.0)
    fecha_ultima_actualizacion: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow)
    stock_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    inventarios: Mapped[list[InventarioBodegaORM]] = relationship(
        back_populates="producto",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class BodegaORM(Base):
    __tablename__ = "bodegas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)

    inventarios: Mapped[list[InventarioBodegaORM]] = relationship(
        back_populates="bodega",
        lazy="selectin",
    )


class InventarioBodegaORM(Base):
    __tablename__ = "inventario_bodega"

    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id", ondelete="CASCADE"), primary_key=True)
    bodega_id: Mapped[int] = mapped_column(ForeignKey("bodegas.id", ondelete="RESTRICT"), primary_key=True)
    cantidad_disponible: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    pasillo: Mapped[str] = mapped_column(String(50), default="")
    estante: Mapped[str] = mapped_column(String(50), default="")

    producto: Mapped[ProductoORM] = relationship(back_populates="inventarios")
    bodega: Mapped[BodegaORM] = relationship(back_populates="inventarios")


def create_sql_engine(db_url: str):
    return create_engine(db_url, future=True, pool_pre_ping=True)


def create_session_factory(db_url: str) -> sessionmaker[Session]:
    engine = create_sql_engine(db_url)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, class_=Session)


def _to_domain(prod: ProductoORM) -> ProductoDomain:
    bodegas: list[BodegaDomain] = []
    for inv in prod.inventarios or []:
        bodegas.append(
            BodegaDomain(
                id=inv.bodega_id,
                nombre=inv.bodega.nombre if inv.bodega else "",
                cantidad_disponible=inv.cantidad_disponible,
                pasillo=inv.pasillo or "",
                estante=inv.estante or "",
            )
        )
    stock_total = sum(b.cantidad_disponible for b in bodegas)
    return ProductoDomain(
        id=prod.id,
        nombre=prod.nombre,
        lote=prod.lote,
        sku=prod.sku,
        stock_total=stock_total,
        stock_minimo=prod.stock_minimo,
        bodegas=bodegas,
        fecha_ultima_actualizacion=prod.fecha_ultima_actualizacion,
        proveedor=prod.proveedor,
        categoria=prod.categoria,
        valor_unitario=prod.valor_unitario,
    )


class SqlProductoRepo(ProductoInventarioRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def list(self, q: Optional[str] = None) -> List[ProductoDomain]:
        stmt = select(ProductoORM).options(joinedload(ProductoORM.inventarios).joinedload(InventarioBodegaORM.bodega))
        if q:
            like = f"%{q.lower()}%"
            stmt = stmt.where(
                func.lower(ProductoORM.nombre).like(like)
                | func.lower(ProductoORM.sku).like(like)
                | func.lower(ProductoORM.lote).like(like)
                | func.lower(ProductoORM.proveedor).like(like)
                | func.lower(ProductoORM.categoria).like(like)
            )
        stmt = stmt.order_by(ProductoORM.id.asc())
        productos = self.session.execute(stmt).scalars().unique().all()
        return [_to_domain(p) for p in productos]

    def get(self, producto_id: int) -> Optional[ProductoDomain]:
        stmt = (
            select(ProductoORM)
            .options(joinedload(ProductoORM.inventarios).joinedload(InventarioBodegaORM.bodega))
            .where(ProductoORM.id == producto_id)
        )
        prod = self.session.execute(stmt).scalars().first()
        return _to_domain(prod) if prod else None

    def save(self, producto: ProductoDomain) -> None:
        # Upsert producto
        prod = self.session.get(ProductoORM, producto.id) if producto.id else None
        if not prod:
            # If producto.id is None, let the DB autogenerate it by not setting id
            if producto.id is None:
                prod = ProductoORM()
            else:
                prod = ProductoORM(id=producto.id)
            self.session.add(prod)

        # Update fields
        prod.nombre = producto.nombre
        prod.lote = producto.lote
        prod.sku = producto.sku
        prod.stock_minimo = producto.stock_minimo
        prod.proveedor = producto.proveedor
        prod.categoria = producto.categoria
        prod.valor_unitario = float(producto.valor_unitario or 0.0)
        prod.fecha_ultima_actualizacion = producto.fecha_ultima_actualizacion or datetime.utcnow()

        # Sync bodegas and inventory entries
        # Ensure bodegas master exist
        bodega_ids = {b.id for b in producto.bodegas}
        if bodega_ids:
            existing = {
                b.id: b for b in self.session.execute(select(BodegaORM).where(BodegaORM.id.in_(list(bodega_ids)))).scalars().all()
            }
        else:
            existing = {}

        # Create missing bodegas
        for b in producto.bodegas:
            if b.id not in existing:
                self.session.add(BodegaORM(id=b.id, nombre=b.nombre))

        # Replace inventory entries
        # Flush to ensure prod.id is available
        self.session.flush()
        # Sync generated id back to domain entity
        if not producto.id:
            producto.id = prod.id
        prod.inventarios.clear()
        for b in producto.bodegas:
            inv = InventarioBodegaORM(
                producto_id=prod.id,
                bodega_id=b.id,
                cantidad_disponible=b.cantidad_disponible,
                pasillo=b.pasillo,
                estante=b.estante,
            )
            prod.inventarios.append(inv)

        # Compute and persist stock_total
        prod.stock_total = sum(b.cantidad_disponible for b in producto.bodegas)


class PostgresUnitOfWork(UnitOfWork):
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory
        self.session: Optional[Session] = None
        self.productos: SqlProductoRepo

    def __enter__(self) -> "PostgresUnitOfWork":
        self.session = self._session_factory()
        self.productos = SqlProductoRepo(self.session)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if not self.session:
            return
        try:
            if exc:
                self.session.rollback()
            else:
                self.session.commit()
        finally:
            self.session.close()

    def commit(self) -> None:
        if self.session:
            self.session.commit()

    def rollback(self) -> None:
        if self.session:
            self.session.rollback()


def build_uow_from_env() -> UnitOfWork | None:
    """
    If INVENTARIO_DATABASE_URL is defined, return a PostgresUnitOfWork; otherwise None.
    """

    DB_USER = os.getenv("DB_USER", "inventario")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "inventario")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "inventario")
    db_url = f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    if not db_url:
        return None
    SessionFactory = create_session_factory(db_url)
    return PostgresUnitOfWork(SessionFactory)
