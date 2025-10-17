from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_healthz():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_listar_productos():
    r = client.get("/inventario/productos")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 5
    first = data[0]
    # Ensure camelCase keys
    for key in [
        "id",
        "nombre",
        "lote",
        "sku",
        "stockTotal",
        "stockMinimo",
        "status",
        "bodegas",
        "fechaUltimaActualizacion",
        "proveedor",
        "categoria",
        "valorUnitario",
    ]:
        assert key in first


def test_obtener_producto():
    r = client.get("/inventario/productos/1")
    assert r.status_code == 200
    prod = r.json()
    assert prod["id"] == 1
    assert prod["sku"] == "PAR500-001"
