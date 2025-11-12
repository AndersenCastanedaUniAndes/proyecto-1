import pytest
from fastapi.testclient import TestClient
from fastapi import status, FastAPI
from unittest.mock import MagicMock
from app.routes.routes import router


# ===============================================================
# 🚀 Configuración del cliente de pruebas
# ===============================================================
app = FastAPI()
app.include_router(router)
client = TestClient(app)


# ===============================================================
# 📦 FIXTURES
# ===============================================================
@pytest.fixture
def mock_db(monkeypatch):
    """Simula la sesión de base de datos"""
    db = MagicMock()
    monkeypatch.setattr("app.models.databases.get_db", lambda: db)
    return db


@pytest.fixture
def mock_crud(monkeypatch):
    """Simula las operaciones CRUD del servicio"""
    mock = MagicMock()
    monkeypatch.setattr("app.routes.routes.crud", mock)
    return mock


# ===============================================================
# 📦 TESTS: PEDIDOS
# ===============================================================
def test_get_pedidos(mock_db, mock_crud):
    mock_crud.get_pedidos.return_value = [
        {
            "id": 1,
            "cliente": "Juan Pérez",
            "direccion": "Calle 123",
            "latitud": 4.65,
            "longitud": -74.05,
            "volumen": 12.5,
            "peso": 8.3,
            "ventana_inicio": "08:00",
            "ventana_fin": "10:00",
            "productos": ["Cajas", "Botellas"],
            "valor": 250000,
            "seleccionado": False,
            "fecha_creacion": "2025-11-12T18:05:08.323Z",
        }
    ]

    response = client.get("/pedidos")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]["cliente"] == "Juan Pérez"
    mock_crud.get_pedidos.assert_called_once()


def test_create_pedido(mock_db, mock_crud):
    # ✅ Debe coincidir con los nombres de PedidoCreate (ventanaInicio, ventanaFin)
    pedido_data_in = {
        "cliente": "Carlos Gómez",
        "direccion": "Carrera 45",
        "latitud": 4.61,
        "longitud": -74.08,
        "volumen": 10.0,
        "peso": 5.5,
        "ventanaInicio": "09:00",
        "ventanaFin": "12:00",
        "productos": ["Zapatos"],
        "valor": 500000,
        "seleccionado": True,
    }

    pedido_data_out = {
        **pedido_data_in,
        "id": 1,
        "fecha_creacion": "2025-11-12T18:05:08.323Z",
    }

    mock_crud.create_pedido.return_value = pedido_data_out
    response = client.post("/pedidos", json=pedido_data_in)

    assert response.status_code == 201
    assert response.json()["cliente"] == "Carlos Gómez"
    mock_crud.create_pedido.assert_called_once()


def test_get_pedido_not_found(mock_db, mock_crud):
    mock_crud.get_pedido.return_value = None
    response = client.get("/pedidos/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Pedido no encontrado"


# ===============================================================
# 🚚 TESTS: PUNTOS DE ENTREGA
# ===============================================================
def test_get_puntos_entrega(mock_db, mock_crud):
    mock_crud.get_puntos_entrega.return_value = [
        {
            "id": 1,
            "pedido_id": 1,
            "direccion": "Carrera 12 #34-56",
            "latitud": 4.65,
            "longitud": -74.07,
            "estado": "pendiente",
            "hora_estimada": "10:30",
            "hora_real": "10:40",
            "observaciones": "Cliente no respondió al primer intento",
        }
    ]

    response = client.get("/puntos-entrega")

    assert response.status_code == 200
    data = response.json()[0]
    assert data["direccion"] == "Carrera 12 #34-56"
    assert data["estado"] == "pendiente"


def test_create_punto_entrega(mock_db, mock_crud):
    # ✅ coincide con PuntoEntregaCreate (pedidoId, horaEstimada, horaReal)
    punto_data_in = {
        "pedidoId": 1,
        "direccion": "Avenida 68 #45-20",
        "latitud": 4.62,
        "longitud": -74.09,
        "estado": "pendiente",
        "horaEstimada": "11:00",
        "horaReal": "11:15",
        "observaciones": "Entregado en portería",
    }

    punto_data_out = {
        **punto_data_in,
        "id": 1,
    }

    mock_crud.create_punto_entrega.return_value = punto_data_out
    response = client.post("/puntos-entrega", json=punto_data_in)

    assert response.status_code == 201
    assert response.json()["direccion"] == "Avenida 68 #45-20"
    mock_crud.create_punto_entrega.assert_called_once()


def test_get_punto_entrega_not_found(mock_db, mock_crud):
    mock_crud.get_punto_entrega.return_value = None
    response = client.get("/puntos-entrega/10")

    assert response.status_code == 404
    assert response.json()["detail"] == "Punto de entrega no encontrado"


# ===============================================================
# 🚛 TESTS: RUTAS DE ENTREGA
# ===============================================================
def test_get_rutas_entrega(mock_db, mock_crud):
    mock_crud.get_rutas_entrega.return_value = [
        {
            "id": 1,
            "nombre": "Ruta Norte",
            "conductor": "Pedro López",
            "vehiculo": "Camión A123",
            "capacidad_volumen": 500,
            "capacidad_peso": 1000,
            "temperatura_controlada": True,
            "fecha_ruta": "2025-11-13",
            "hora_inicio": "07:00",
            "estado": "planificada",
            "fecha_creacion": "2025-11-12T18:12:55.756Z",
            "distancia_total": 120.5,
            "tiempo_estimado": 180,
        }
    ]

    response = client.get("/rutas-entrega")

    assert response.status_code == 200
    data = response.json()[0]
    assert data["nombre"] == "Ruta Norte"
    assert data["vehiculo"] == "Camión A123"
    assert data["temperatura_controlada"] is True


def test_create_ruta_entrega(mock_db, mock_crud):
    # Request (input): usa camelCase como en RutaEntregaCreate
    ruta_data_in = {
        "nombre": "Ruta Sur",
        "conductor": "María García",
        "vehiculo": "Camión B456",
        "capacidadVolumen": 300,
        "capacidadPeso": 800,
        "temperaturaControlada": False,
        "fechaRuta": "2025-11-14",
        "horaInicio": "08:30",
        "estado": "planificada",
        "distanciaTotal": 95.4,
        "tiempoEstimado": 150,
    }

    # Mock CRUD (output): usa los alias snake_case esperados por RutaEntregaOut
    ruta_data_out = {
        "id": 1,
        "nombre": "Ruta Sur",
        "conductor": "María García",
        "vehiculo": "Camión B456",
        "capacidad_volumen": 300,
        "capacidad_peso": 800,
        "temperatura_controlada": False,
        "fecha_ruta": "2025-11-14",
        "hora_inicio": "08:30",
        "estado": "planificada",
        "fecha_creacion": "2025-11-12T18:12:55.756Z",
        "distancia_total": 95.4,
        "tiempo_estimado": 150,
    }

    mock_crud.create_ruta_entrega.return_value = ruta_data_out
    response = client.post("/rutas-entrega", json=ruta_data_in)

    assert response.status_code == 201
    data = response.json()
    assert data["conductor"] == "María García"
    assert data["estado"] == "planificada"
    assert data["vehiculo"] == "Camión B456"



def test_get_ruta_entrega_not_found(mock_db, mock_crud):
    mock_crud.get_ruta_entrega.return_value = None
    response = client.get("/rutas-entrega/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Ruta de entrega no encontrada"
