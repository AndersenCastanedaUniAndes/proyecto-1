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

    # Si no hay productos, solo verificamos que la lista esté vacía
    if len(data) == 0:
        print("⚠️ No hay productos registrados en el inventario.")
        return

    # Si hay productos, verificamos que tengan las claves esperadas
    first = data[0]
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

    # Si no existe el producto (caso normal en DB vacía)
    if r.status_code == 404:
        data = r.json()
        assert "detail" in data
        assert data["detail"] == "Producto no encontrado"
        print("✅ Producto no encontrado (404) validado correctamente.")
        return

    # Si el producto existe
    assert r.status_code == 200
    prod = r.json()
    assert isinstance(prod, dict)
    assert "id" in prod
    assert "sku" in prod
    assert isinstance(prod["id"], int)
    assert isinstance(prod["sku"], str)

    # Validación adicional opcional si se conoce el producto
    if prod["id"] == 1:
        assert prod["sku"] == "PAR500-001"


