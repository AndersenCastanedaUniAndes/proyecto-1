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
from ..domain.models import BodegaDetalle as BodegaDetalleDomain
from ..domain.models import ProductoInventario as ProductoDomain
from ..domain.repositories import BodegaRepository, ProductoInventarioRepository, UnitOfWork


class Base(DeclarativeBase):
    pass


class ProductoORM(Base):
    __tablename__ = "inventario_productos"

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

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    direccion: Mapped[str] = mapped_column(String(255), default="")

    inventarios: Mapped[list[InventarioBodegaORM]] = relationship(
        back_populates="bodega",
        lazy="selectin",
    )


class InventarioBodegaORM(Base):
    __tablename__ = "inventario_bodega"

    producto_id: Mapped[int] = mapped_column(ForeignKey("inventario_productos.id", ondelete="CASCADE"), primary_key=True)
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
    bodegas_detalle: list[BodegaDetalleDomain] = []

    for inv in prod.inventarios or []:
        if inv.bodega:
            bodegas_detalle.append(
                BodegaDetalleDomain(
                    id=inv.bodega.id,
                    nombre=inv.bodega.nombre,
                    direccion=inv.bodega.direccion or "",
                    cantidad_disponible=inv.cantidad_disponible,
                    pasillo=inv.pasillo,
                    estante=inv.estante,
                )
            )

    stock_total = sum(inv.cantidad_disponible for inv in prod.inventarios or [])

    return ProductoDomain(
        id=prod.id,
        nombre=prod.nombre,
        lote=prod.lote,
        sku=prod.sku,
        stock_total=stock_total,
        stock_minimo=prod.stock_minimo,
        bodegas=bodegas_detalle,
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
        prod = self.session.get(ProductoORM, producto.id) if producto.id else None

        if not prod:
            if producto.id is None:
                prod = ProductoORM()
            else:
                prod = ProductoORM(id=producto.id)

            self.session.add(prod)

        prod.nombre = producto.nombre
        prod.lote = producto.lote
        prod.sku = producto.sku
        prod.stock_minimo = producto.stock_minimo
        prod.proveedor = producto.proveedor
        prod.categoria = producto.categoria
        prod.valor_unitario = float(producto.valor_unitario or 0.0)
        prod.fecha_ultima_actualizacion = producto.fecha_ultima_actualizacion or datetime.utcnow()

        bodega_ids = {b.id for b in producto.bodegas if b.id is not None}
        if bodega_ids:
            existing = {
                b.id: b for b in self.session.execute(select(BodegaORM).where(BodegaORM.id.in_(list(bodega_ids)))).scalars().all()
            }
        else:
            existing = {}

        for b in producto.bodegas:
            if b.id is None:
                orm_bodega = BodegaORM(nombre=b.nombre, direccion=b.direccion)
                self.session.add(orm_bodega)
                self.session.flush()
                b.id = orm_bodega.id
                existing[b.id] = orm_bodega
            elif b.id not in existing:
                orm_bodega = BodegaORM(id=b.id, nombre=b.nombre, direccion=b.direccion)
                self.session.add(orm_bodega)
                existing[b.id] = orm_bodega

        self.session.flush()

        if not producto.id:
            producto.id = prod.id

        for inv in list(prod.inventarios):
            self.session.delete(inv)
        prod.inventarios.clear()

        for detalle in producto.bodegas:
            if detalle.id is None:
                continue

            inv = InventarioBodegaORM(
                producto_id=producto.id,
                bodega_id=detalle.id,
                cantidad_disponible=detalle.cantidad_disponible,
                pasillo=detalle.pasillo,
                estante=detalle.estante,
            )
            prod.inventarios.append(inv)

        prod.stock_total = sum(inv.cantidad_disponible for inv in prod.inventarios)


class SqlBodegaRepo(BodegaRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def list(self) -> list[BodegaDomain]:
        bodegas = self.session.execute(select(BodegaORM)).scalars().all()
        return [BodegaDomain(id=b.id, nombre=b.nombre, direccion=b.direccion or "") for b in bodegas]

    def get(self, bodega_id: int) -> BodegaDomain | None:
        b = self.session.get(BodegaORM, bodega_id)
        if not b:
            return None
        return BodegaDomain(id=b.id, nombre=b.nombre, direccion=b.direccion or "")

    def create(self, bodega: BodegaDomain) -> BodegaDomain:
        orm = BodegaORM(nombre=bodega.nombre, direccion=bodega.direccion)
        self.session.add(orm)
        self.session.flush()
        return BodegaDomain(id=orm.id, nombre=orm.nombre, direccion=orm.direccion or "")


class PostgresUnitOfWork(UnitOfWork):
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory
        self.session: Optional[Session] = None
        self.productos: SqlProductoRepo
        self.bodegas: SqlBodegaRepo

    def __enter__(self) -> "PostgresUnitOfWork":
        self.session = self._session_factory()
        self.productos = SqlProductoRepo(self.session)
        self.bodegas = SqlBodegaRepo(self.session)
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
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
    DB_HOST = os.getenv("DB_HOST", "34.58.178.152")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "postgres")
    db_url = f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    print(f"Connecting to {db_url}")

    if not db_url:
        return None

    SessionFactory = create_session_factory(db_url)
    return PostgresUnitOfWork(SessionFactory)