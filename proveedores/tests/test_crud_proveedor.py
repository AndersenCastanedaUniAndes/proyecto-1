import pytest
from datetime import datetime
from sqlalchemy import create_engine,text
from sqlalchemy.orm import sessionmaker
from app.models.databases import Base
from app.models.models import Proveedor
from app.models import models
from app.services import crud
from app.models.proveedor import ProveedorUpdate


# ---------------------------------------------------------------------
# FIXTURES
# ---------------------------------------------------------------------

@pytest.fixture(scope="module")
def test_db():
    DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/proveedores"
    engine = create_engine(DATABASE_URL, echo=False)

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # 🔹 Reiniciar secuencia del campo id (importante)
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM proveedor;"))  # elimina todos los registros
        conn.execute(text("ALTER SEQUENCE proveedor_id_seq RESTART WITH 100;"))  # reinicia IDs desde 100
        conn.commit()

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    yield db

    db.rollback()
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def proveedor_data():
    """Datos base para las pruebas."""
    return {
        #"id":1,
        "nombre": "Proveedor Test",
        "correoElectronico": "test@mail.com",
        "estado": "Activo",
        "fechaCreacion": datetime.utcnow(),
    }


# ---------------------------------------------------------------------
# TESTS CRUD
# ---------------------------------------------------------------------
def test_create_proveedor(test_db, proveedor_data):
    """Debe crear un proveedor correctamente."""
    proveedor = models.Proveedor(**proveedor_data)
    result = crud.create_proveedor(test_db, proveedor)

    assert result.id is not None
    assert result.nombre == proveedor_data["nombre"]
    assert result.correoElectronico == proveedor_data["correoElectronico"]
    assert result.estado == "Activo"
    assert isinstance(result.fechaCreacion, datetime)


def test_get_proveedor(test_db, proveedor_data):
    """Debe obtener un proveedor por su ID."""
    nuevo = models.Proveedor(**proveedor_data)
    creado = crud.create_proveedor(test_db, nuevo)

    result = crud.get_proveedor(test_db, creado.id)
    assert result is not None
    assert result.id == creado.id
    assert result.nombre == proveedor_data["nombre"]


def test_get_proveedores(test_db, proveedor_data):
    """Debe listar todos los proveedores registrados."""
    crud.create_proveedor(test_db, models.Proveedor(**proveedor_data))
    result = crud.get_proveedores(test_db)
    assert isinstance(result, list)
    assert len(result) >= 1
    assert all(isinstance(p, models.Proveedor) for p in result)


def test_update_proveedor(test_db, proveedor_data):
    creado = crud.create_proveedor(test_db, models.Proveedor(**proveedor_data))

    proveedor_update = ProveedorUpdate(
        nombre="Proveedor Actualizado",
        correoElectronico="nuevo@mail.com",
        estado="Inactivo",
        fechaCreacion=creado.fechaCreacion
    )

    actualizado = crud.update_proveedor(test_db, creado, proveedor_update)

    assert actualizado.nombre == "Proveedor Actualizado"
    assert actualizado.correoElectronico == "nuevo@mail.com"
    assert actualizado.estado == "Inactivo"

def test_delete_proveedor(test_db, proveedor_data):
    """Debe eliminar un proveedor correctamente."""
    creado = crud.create_proveedor(test_db, models.Proveedor(**proveedor_data))
    crud.delete_proveedor(test_db, creado)

    result = crud.get_proveedor(test_db, creado.id)
    assert result is None


# ---------------------------------------------------------------------
# TEST init_db
# ---------------------------------------------------------------------
def test_init_db(monkeypatch):
    """Debe ejecutar init_db correctamente sin lanzar excepción."""
    called = {}

    def mock_create_all(bind=None):
        called["ok"] = True

    monkeypatch.setattr(crud.Base.metadata, "create_all", mock_create_all)
    crud.init_db()
    assert "ok" in called
