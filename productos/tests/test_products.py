import pytest
from unittest.mock import MagicMock, AsyncMock
from datetime import timedelta, datetime
from fastapi import HTTPException, UploadFile
from jose import jwt
import pandas as pd
from io import BytesIO


from app.services import crud  # Ajusta el import al path real
from config.config import SECRET_KEY, ALGORITHM


# -------------------------------
# 🔹 PRUEBAS DE UTILIDADES BÁSICAS
# -------------------------------

def test_hash_and_verify_password():
    password = "superseguro123"
    hashed = crud.hash_password(password)

    assert hashed != password
    assert crud.verify_password(password, hashed)
    assert not crud.verify_password("incorrecta", hashed)


def test_create_access_token():
    data = {"sub": "usuario1"}
    token = crud.create_access_token(data, timedelta(minutes=5))
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert decoded["sub"] == "usuario1"
    assert "exp" in decoded


def test_create_access_token_fails(monkeypatch):
    def fail_encode(*args, **kwargs):
        raise Exception("falló")

    monkeypatch.setattr(crud.jwt, "encode", fail_encode)

    with pytest.raises(HTTPException) as exc:
        crud.create_access_token({"sub": "test"})
    assert "Error al crear el token" in str(exc.value.detail)


# -------------------------------
# 🔹 PRUEBAS DE FUNCIONES CRUD
# -------------------------------

def test_get_producto(monkeypatch):
    mock_db = MagicMock()
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = "producto_mock"

    result = crud.get_producto(mock_db, 1)
    assert result == "producto_mock"
    mock_query.filter.assert_called_once()


def test_get_productos(monkeypatch):
    mock_db = MagicMock()
    mock_query = mock_db.query.return_value
    mock_query.offset.return_value.limit.return_value.all.return_value = ["p1", "p2"]

    result = crud.get_productos(mock_db)
    assert len(result) == 2
    mock_query.offset.assert_called_once_with(0)


def test_create_producto(monkeypatch):
    mock_db = MagicMock()
    producto = MagicMock()
    producto.nombre = "Producto X"
    producto.lote = "L123"
    producto.numeroSerial = "SN001"
    producto.proveedor = "Proveedor X"
    producto.precioUnidad = 10.5
    producto.precioTotal = 105.0
    producto.paisOrigen = "Colombia"
    producto.uom = "unidad"
    producto.cantidad = 10
    producto.tipoAlmacenamiento = "seco"
    producto.temperaturaMin = 5.0
    producto.temperaturaMax = 25.0

    result = crud.create_producto(mock_db, producto)

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()
    assert result == mock_db.refresh.call_args[0][0]


# -------------------------------
# 🔹 PRUEBAS DE FUNCIONES ESTÁTICAS
# -------------------------------

def test_get_paises_ordered():
    paises = crud.get_paises()
    assert isinstance(paises, list)
    assert paises == sorted(paises, key=lambda p: p.lower())
    assert "Colombia" in paises


def test_get_uom_ordered():
    uoms = crud.get_uom()
    assert uoms == sorted(uoms, key=lambda p: p.lower())
    assert "unidad" in uoms


def test_get_proveedores_ordered():
    proveedores = crud.get_proveedores()
    assert proveedores == sorted(proveedores, key=lambda p: p.lower())
    assert "Laboratorios Pharma Plus" in proveedores


def test_get_tipo_almacenamiento_ordered():
    tipos = crud.get_tipo_almacenamiento()
    assert tipos == sorted(tipos, key=lambda p: p.lower())
    assert "seco" in tipos


# -------------------------------
# 🔹 PRUEBAS ASÍNCRONAS: CARGA DE EXCEL
# -------------------------------

@pytest.mark.asyncio
async def test_get_productos_creados(monkeypatch):
    # Crear DataFrame simulado
    data = {
        "nombre": ["P1"],
        "lote": ["L1"],
        "numeroSerial": ["S1"],
        "proveedor": ["Prov1"],
        "precioUnidad": [10],
        "precioTotal": [100],
        "paisOrigen": ["Colombia"],
        "uom": ["unidad"],
        "cantidad": [5],
        "tipoAlmacenamiento": ["seco"],
        "temperaturaMin": [2],
        "temperaturaMax": [8],
    }
    df = pd.DataFrame(data)

    # Guardar en bytes (como si fuera Excel)
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False)
    buffer.seek(0)

    mock_file = UploadFile(filename="productos.xlsx", file=buffer)

    mock_db = MagicMock()
    monkeypatch.setattr(crud, "get_producto_by_serial", lambda db, s: None)
    monkeypatch.setattr(crud, "create_producto", lambda db, p: p)

    result = await crud.get_productos_creados(mock_file, mock_db)

    assert "productos cargados exitosamente" in result["mensaje"]


@pytest.mark.asyncio
async def test_get_productos_creados_invalid_file():
    mock_file = UploadFile(filename="archivo.txt", file=BytesIO(b"contenido de prueba"))
    with pytest.raises(HTTPException) as exc:
        await crud.get_productos_creados(mock_file, MagicMock())
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_get_productos_creados_missing_column(monkeypatch):
    df = pd.DataFrame({"nombre": ["P1"]})
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False)
    buffer.seek(0)

    mock_file = UploadFile(filename="productos.xlsx", file=buffer)

    async def fake_read():
        return buffer.getvalue()

    mock_file.read = fake_read

    with pytest.raises(HTTPException) as exc:
        await crud.get_productos_creados(mock_file, MagicMock())
    assert "Columna faltante" in exc.value.detail
  