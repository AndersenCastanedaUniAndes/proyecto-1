import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from datetime import date
from fastapi import FastAPI
from app.routes.routes import router  # importa tu router principal de ventas
from app.models.ventas import VentaOut



class TestVentasRouter(unittest.TestCase):
    def setUp(self):
        app = FastAPI()
        app.include_router(router, prefix="/ventas")  # usa el prefijo correcto
        self.client = TestClient(app)

        self.venta_data = {
            "id": 1,
            "fecha": str(date.today()),
            "vendedor": "admin2_ventas",
            "vendedor_id": 1,
            "producto": "Paracetamol 500mg",
            "producto_id": 8,
            "cantidad": 200,
            "valor_unitario": 0.15,
            "valor_total": 30.0,
            "cliente": "Clínica Vida Plena",
            "comision": 12.0,
            "cliente_id": 5,        # ← AGREGAR
            "productos": [],        # ← AGREGAR (según tu modelo)
            "estado": "activo",     # ← AGREGAR
            "comision": 12.0,
        }
    # ---------- GET / ----------
    @patch("app.routes.routes.crud.get_ventas")
    def test_get_ventas_ok(self, mock_get_ventas):

        self.venta_data["productos"] = [
            {
                "producto": "Paracetamol 500mg",
                "producto_id": 8,
                "cantidad": 200,
                "valor_unitario": 0.15
            }
        ]

        mock_get_ventas.return_value = [self.venta_data]

        response = self.client.get("/ventas/")
        self.assertEqual(response.status_code, 200)

        ventas = response.json()
        self.assertIsInstance(ventas, list)

        self.assertEqual(
            ventas[0]["productos"][0]["producto"],
            "Paracetamol 500mg"
        )

        mock_get_ventas.assert_called_once()

    

    # ---------- POST / ----------
    @patch("app.routes.routes.crud.create_venta")
    def test_create_venta(self, mock_create):

        venta_in = {
            "fecha": str(date.today()),
            "vendedor": "admin2_ventas",
            "vendedor_id": 1,
            "productos": [
                {
                    "producto": "Paracetamol 500mg",
                    "producto_id": 8,
                    "cantidad": 200,
                    "valor_unitario": 0.15
                }
            ],
            "cliente": "Clínica Vida Plena",
            "cliente_id": 5,
            "comision": 12.0
        }

        venta_out = {
            "id": 1,
            "fecha": str(date.today()),
            "vendedor": "admin2_ventas",
            "vendedor_id": 1,
            "productos": [
                {
                    "producto": "Paracetamol 500mg",
                    "producto_id": 8,
                    "cantidad": 200,
                    "valor_unitario": 0.15
                }
            ],
            "cliente": "Clínica Vida Plena",
            "cliente_id": 5,
            "comision": 12.0,
            "estado": "activo"
        }

        mock_create.return_value = venta_out

        response = self.client.post("/ventas/", json=venta_in)

        self.assertEqual(response.status_code, 201)
        data = response.json()

        self.assertEqual(data["cliente"], venta_in["cliente"])
        self.assertEqual(data["cliente_id"], venta_in["cliente_id"])
        self.assertEqual(data["productos"][0]["producto"], "Paracetamol 500mg")

        mock_create.assert_called_once()

    # ---------- GET /{id} ----------
    @patch("app.routes.routes.crud.get_venta")
    def test_get_venta_encontrada(self, mock_get_venta):
        mock_get_venta.return_value = self.venta_data
        response = self.client.get("/ventas/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], 1)

    @patch("app.routes.routes.crud.get_venta")
    def test_get_venta_no_encontrada(self, mock_get_venta):
        """❌ Prueba cuando la venta no existe"""
        mock_get_venta.return_value = None

        response = self.client.get("/ventas/99")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Venta no encontrada")


    # ---------- PUT /{id} ----------


    # ---------- DELETE /{id} ----------
    @patch("app.routes.routes.crud.delete_venta")
    @patch("app.routes.routes.crud.get_venta")
    def test_delete_venta_ok(self, mock_get_venta, mock_delete_venta):
        mock_get_venta.return_value = self.venta_data
        response = self.client.delete("/ventas/1")
        self.assertEqual(response.status_code, 204)
        mock_delete_venta.assert_called_once()

    @patch("app.routes.routes.crud.get_venta")
    def test_delete_venta_no_encontrada(self, mock_get_venta):
        """❌ Prueba eliminación cuando la venta no existe"""
        mock_get_venta.return_value = None

        response = self.client.delete("/ventas/99")

        self.assertEqual(response.status_code, 404)

