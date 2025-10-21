import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, ANY
from datetime import datetime

from app.main import app  # Asegúrate de tener tu instancia FastAPI principal aquí

# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------

@pytest.fixture
def client():
    """Cliente de prueba de FastAPI."""
    return TestClient(app)


# ---------------------------------------------------------------------
# Tests para endpoints del router proveedor
# ---------------------------------------------------------------------

@patch("app.services.crud.get_proveedores")
def test_get_proveedores(mock_get, client):
    """Debe retornar una lista de proveedores."""
    mock_get.return_value = [
        {
            "id": 1,
            "nombre": "Proveedor X",
            "correoElectronico": "x@mail.com",
            "estado": "Activo",
            "fechaCreacion": "2024-01-01"
        }
    ]

    response = client.get("/proveedores/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.json()[0]["nombre"] == "Proveedor X"
    mock_get.assert_called_once()


@patch("app.services.crud.create_proveedor")
def test_create_proveedor_con_fecha(mock_create, client):
    """Debe crear un proveedor cuando se envía la fecha."""
    proveedor = {
        "nombre": "Proveedor Y",
        "correoElectronico": "y@mail.com",
        "estado": "Activo",
        "fechaCreacion": "2024-05-01"
    }

    mock_create.return_value = {
        "id": 1,
        **proveedor
    }

    response = client.post("/proveedores/", json=proveedor)
    assert response.status_code == 201
    assert response.json()["nombre"] == "Proveedor Y"
    mock_create.assert_called_once()

@patch("app.services.crud.create_proveedor")
def test_create_proveedor_sin_fecha(mock_create, client):
    """Debe asignar la fecha actual si no se envía."""
    proveedor = {
        "nombre": "Proveedor Z",
        "correoElectronico": "z@mail.com",
        "estado": "Activo"
    }

    mock_create.return_value = {
        "id": 2,
        **proveedor,
        "fechaCreacion": datetime.utcnow().strftime("%Y-%m-%d")
    }

    response = client.post("/proveedores/", json=proveedor)
    assert response.status_code == 201
    data = response.json()
    assert "fechaCreacion" in data
    mock_create.assert_called_once()

@patch("app.services.crud.get_proveedor")
def test_get_proveedor_existente(mock_get, client):
    """Debe retornar un proveedor existente."""
    mock_get.return_value = {
        "id": 1,
        "nombre": "Proveedor A",
        "correoElectronico": "a@mail.com",
        "estado": "Activo",
        "fechaCreacion": "2024-01-01"
    }

    response = client.get("/proveedores/1")
    assert response.status_code == 200
    assert response.json()["nombre"] == "Proveedor A"
    mock_get.assert_called_once_with(ANY, 1)


@patch("app.services.crud.get_proveedor")
def test_get_proveedor_no_encontrado(mock_get, client):
    """Debe retornar 404 si el proveedor no existe."""
    mock_get.return_value = None

    response = client.get("/proveedores/99")
    assert response.status_code == 404
    assert response.json()["detail"] == "Proveedor no encontrado"


@patch("app.services.crud.get_proveedor")
@patch("app.services.crud.update_proveedor")
def test_update_proveedor(mock_update, mock_get, client):
    """Debe actualizar un proveedor existente."""

    mock_get.return_value = {
        "id": 1,
        "nombre": "Antiguo",
        "correoElectronico": "antiguo@mail.com",
        "estado": "Inactivo",
        "fechaCreacion": datetime.utcnow().isoformat()
    }

    mock_update.return_value = {
        "id": 1,
        "nombre": "Nuevo",
        "correoElectronico": "nuevo@mail.com",
        "estado": "Activo",
        "fechaCreacion": datetime.utcnow().isoformat()
    }

    proveedor_in = {
        "nombre": "Nuevo",
        "correoElectronico": "nuevo@mail.com",
        "estado": "Activo"
    }

    response = client.put("/proveedores/1", json=proveedor_in)

    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Nuevo"
    assert data["correoElectronico"] == "nuevo@mail.com"
    assert data["estado"] == "Activo"
    assert "fechaCreacion" in data

    mock_get.assert_called_once_with(ANY, 1)
    mock_update.assert_called_once()

@patch("app.services.crud.get_proveedor")
@patch("app.services.crud.delete_proveedor")
def test_delete_proveedor(mock_delete, mock_get, client):
    """Debe eliminar un proveedor existente."""
    mock_get.return_value = {"id": 1, "nombre": "Proveedor X"}
    response = client.delete("/proveedores/1")
    assert response.status_code == 204
    mock_delete.assert_called_once()


@patch("app.services.crud.get_proveedor")
def test_delete_proveedor_no_encontrado(mock_get, client):
    """Debe retornar 404 si no existe proveedor a eliminar."""
    mock_get.return_value = None
    response = client.delete("/proveedores/99")
    assert response.status_code == 404
    assert response.json()["detail"] == "Proveedor no encontrado"
