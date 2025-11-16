import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import models
from app.services import crud
from app.models.databases import Base


# ===============================================================
# ⚙️ CONFIGURACIÓN DE DB EN MEMORIA
# ===============================================================
@pytest.fixture(scope="module")
def test_db():
    """Base de datos SQLite en memoria para pruebas."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# ===============================================================
# 📦 TESTS: PEDIDOS
# ===============================================================
def test_create_get_update_delete_pedido(test_db):
    pedido_in = type("PedidoIn", (), {
        "cliente": "Juan Pérez",
        "direccion": "Calle 123",
        "latitud": 4.65,
        "longitud": -74.05,
        "volumen": 12.5,
        "peso": 8.3,
        "ventanaInicio": "08:00",
        "ventanaFin": "10:00",
        "productos": ["Cajas", "Botellas"],
        "valor": 250000,
        "seleccionado": False
    })()

    # Simular método dict() como hace Pydantic
    pedido_in.dict = lambda: pedido_in.__dict__

    # Crear
    pedido = crud.create_pedido(test_db, pedido_in)
    assert pedido.id is not None
    assert pedido.cliente == "Juan Pérez"

    # Obtener uno
    fetched = crud.get_pedido(test_db, pedido.id)
    assert fetched.direccion == "Calle 123"

    # Obtener lista
    lista = crud.get_pedidos(test_db)
    assert len(lista) >= 1

    # Actualizar
    pedido_in.direccion = "Calle 456"
    updated = crud.update_pedido(test_db, fetched, pedido_in)
    assert updated.direccion == "Calle 456"

    # Eliminar
    crud.delete_pedido(test_db, updated)
    assert crud.get_pedido(test_db, updated.id) is None


# ===============================================================
# 🚚 TESTS: PUNTOS DE ENTREGA
# ===============================================================
def test_create_get_update_delete_punto_entrega(test_db):
    # Crear pedido base
    pedido = models.Pedido(
        cliente="Ana",
        direccion="Carrera 10",
        latitud=4.6,
        longitud=-74.1,
        volumen=8.0,
        peso=4.0,
        ventana_inicio="09:00",
        ventana_fin="11:00",
        productos="Leche,Pan",
        valor=150000,
        seleccionado=True,
        fecha_creacion=datetime.now()
    )
    test_db.add(pedido)
    test_db.commit()
    test_db.refresh(pedido)

    punto_in = type("PuntoIn", (), {
        "pedidoId": pedido.id,
        "direccion": "Avenida 68 #45-20",
        "latitud": 4.62,
        "longitud": -74.09,
        "estado": "pendiente",
        "horaEstimada": "11:00",
        "horaReal": "11:15",
        "observaciones": "Entregado en portería"
    })()
    punto_in.dict = lambda: punto_in.__dict__

    # Crear
    punto = crud.create_punto_entrega(test_db, punto_in)
    assert punto.id is not None
    assert punto.estado.value == "pendiente"

    # Obtener uno
    fetched = crud.get_punto_entrega(test_db, punto.id)
    assert fetched.direccion == "Avenida 68 #45-20"

    # Lista
    lista = crud.get_puntos_entrega(test_db)
    assert len(lista) >= 1

    # Actualizar
    punto_in.estado = "entregado"
    updated = crud.update_punto_entrega(test_db, fetched, punto_in)
    assert updated.estado.value == "entregado"

    # Eliminar
    crud.delete_punto_entrega(test_db, updated)
    assert crud.get_punto_entrega(test_db, updated.id) is None


# ===============================================================
# 🚛 TESTS: RUTAS DE ENTREGA
# ===============================================================
def test_create_get_update_delete_ruta_entrega(test_db):
    ruta_in = type("RutaIn", (), {
        "nombre": "Ruta Norte",
        "conductor": "Pedro López",
        "vehiculo": "Camión A123",
        "capacidadVolumen": 500,
        "capacidadPeso": 1000,
        "temperaturaControlada": True,
        "fechaRuta": "2025-11-13",
        "horaInicio": "07:00",
        "estado": "planificada",
        "distanciaTotal": 120.5,
        "tiempoEstimado": 180
    })()
    ruta_in.dict = lambda: ruta_in.__dict__

    # Crear
    ruta = crud.create_ruta_entrega(test_db, ruta_in)
    assert ruta.id is not None
    assert ruta.conductor == "Pedro López"

    # Obtener uno
    fetched = crud.get_ruta_entrega(test_db, ruta.id)
    assert fetched.nombre == "Ruta Norte"

    # Lista
    lista = crud.get_rutas_entrega(test_db)
    assert len(lista) >= 1

    # Actualizar
    ruta_in.estado = "completada"
    updated = crud.update_ruta_entrega(test_db, fetched, ruta_in)
    assert updated.estado.value == "completada"

    # Eliminar
    crud.delete_ruta_entrega(test_db, updated)
    assert crud.get_ruta_entrega(test_db, updated.id) is None
