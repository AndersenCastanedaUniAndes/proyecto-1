import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from unittest.mock import ANY
from app.infrastructure.postgres import (
    SqlProductoRepo, PostgresUnitOfWork, ProductoORM, BodegaORM, InventarioBodegaORM, _to_domain
)
from app.domain.models import ProductoInventario as ProductoDomain, Bodega as BodegaDomain


@pytest.fixture
def mock_session():
    """Mock de sesión SQLAlchemy."""
    return MagicMock()


@pytest.fixture
def sample_producto_domain():
    """Producto de dominio simulado."""
    bodega = BodegaDomain(
        id=1, nombre="Central", cantidad_disponible=10, pasillo="A1", estante="2"
    )
    return ProductoDomain(
        id=None,
        nombre="Producto X",
        lote="L001",
        sku="SKU001",
        stock_minimo=5,
        proveedor="Proveedor SA",
        categoria="General",
        valor_unitario=1000.0,
        stock_total=10,
        bodegas=[bodega],
        fecha_ultima_actualizacion=datetime(2024, 1, 1)
    )


# ---------------------------------------------------------------------------
# Tests para SqlProductoRepo
# ---------------------------------------------------------------------------

 
def test_list_con_filtro(mock_session):
    repo = SqlProductoRepo(mock_session)
    mock_session.execute.return_value.scalars.return_value.unique.return_value.all.return_value = []
    result = repo.list(q="sku")
    mock_session.execute.assert_called_once()
    assert result == []



def test_get_no_existente(mock_session):
    repo = SqlProductoRepo(mock_session)
    mock_session.execute.return_value.scalars.return_value.first.return_value = None
    result = repo.get(99)
    assert result is None


def test_save_nuevo_producto(mock_session, sample_producto_domain):
    repo = SqlProductoRepo(mock_session)
    mock_session.stock_total=10
    mock_session.get.return_value = None
    mock_session.execute.return_value.scalars.return_value.all.return_value = []
    repo.save(sample_producto_domain)

    # Verifica que se haya agregado un nuevo ProductoORM
    mock_session.add.assert_any_call(ANY)


def test_save_producto_existente(mock_session, sample_producto_domain):
    repo = SqlProductoRepo(mock_session)
    producto_existente = ProductoORM(id=1, nombre="Viejo", lote="L1", sku="S1", stock_minimo=1)
    mock_session.get.return_value = producto_existente
    repo.save(sample_producto_domain)
    assert producto_existente.nombre == "Viejo"


# ---------------------------------------------------------------------------
# Tests para PostgresUnitOfWork
# ---------------------------------------------------------------------------

def test_uow_commit_y_exit_correcto(mock_session):
    session_factory = MagicMock(return_value=mock_session)
    uow = PostgresUnitOfWork(session_factory)

    with uow:
        assert isinstance(uow.productos, SqlProductoRepo)
        uow.commit()

    mock_session.commit.assert_called()
    mock_session.close.assert_called()


def test_uow_exit_con_excepcion(mock_session):
    session_factory = MagicMock(return_value=mock_session)
    uow = PostgresUnitOfWork(session_factory)

    with pytest.raises(Exception):
        with uow:
            raise Exception("Error")

    mock_session.rollback.assert_called()
    mock_session.close.assert_called()
