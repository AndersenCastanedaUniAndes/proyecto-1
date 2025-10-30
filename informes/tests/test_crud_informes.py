import unittest
from unittest.mock import MagicMock, patch
from datetime import date
from sqlalchemy.exc import SQLAlchemyError

# Importa directamente el módulo CRUD a probar
from app.services import crud


class TestCRUDVentas(unittest.TestCase):

    def setUp(self):
        """Configura mocks comunes"""
        self.mock_db = MagicMock()
        self.mock_venta = MagicMock()
        self.mock_venta.id = 1
        self.mock_venta.vendedor = "admin"
        self.mock_venta.producto = "Paracetamol"
        self.mock_venta.cliente = "Clínica Salud"
        self.mock_venta.cantidad = 10
        self.mock_venta.valorUnitario = 1000
        self.mock_venta.valorTotal = 10000
        self.mock_venta.comision = 5.0
        self.mock_venta.fecha = date.today()

    # ---------------------------------------------------------------------
    # ✅ TEST: get_venta
    # ---------------------------------------------------------------------
    def test_get_venta_ok(self):
        """Debe retornar una venta cuando existe"""
        # Configuramos el mock de la consulta
        mock_query = self.mock_db.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = self.mock_venta

        venta = crud.get_venta(self.mock_db, 1)

        self.assertEqual(venta.vendedor, "admin")
        self.mock_db.query.assert_called_with(crud.models.Venta)
        mock_query.filter.assert_called_once()
        mock_filter.first.assert_called_once()

    def test_get_venta_none(self):
        """Debe retornar None cuando no existe la venta"""
        self.mock_db.query().filter().first.return_value = None
        venta = crud.get_venta(self.mock_db, 99)
        self.assertIsNone(venta)

    # ---------------------------------------------------------------------
    # ✅ TEST: get_ventas
    # ---------------------------------------------------------------------
    def test_get_ventas_lista(self):
        """Debe retornar una lista de ventas"""
        self.mock_db.query().offset().limit().all.return_value = [self.mock_venta]
        ventas = crud.get_ventas(self.mock_db)
        self.assertEqual(len(ventas), 1)
        self.assertEqual(ventas[0].producto, "Paracetamol")

    def test_get_ventas_vacia(self):
        """Debe retornar lista vacía cuando no hay registros"""
        self.mock_db.query().offset().limit().all.return_value = []
        ventas = crud.get_ventas(self.mock_db)
        self.assertEqual(ventas, [])

    # ---------------------------------------------------------------------
    # ✅ TEST: create_venta
    # ---------------------------------------------------------------------
    @patch("app.services.crud.models.Venta")
    def test_create_venta_ok(self, mock_model):
        """Debe crear y retornar una venta"""
        mock_instance = MagicMock()
        mock_model.return_value = mock_instance

        venta_mock = MagicMock()
        venta_mock.fecha = None
        venta_mock.vendedor = "admin"
        venta_mock.vendedorId = 1
        venta_mock.producto = "Ibuprofeno"
        venta_mock.producto_id = 10
        venta_mock.cantidad = 5
        venta_mock.valorUnitario = 2000
        venta_mock.valorTotal = 10000
        venta_mock.cliente = "Farmacia Uno"
        venta_mock.comision = 3.0

        result = crud.create_venta(self.mock_db, venta_mock)

        mock_model.assert_called_once()
        self.mock_db.add.assert_called_once()
        self.mock_db.commit.assert_called_once()
        self.mock_db.refresh.assert_called_once_with(mock_instance)
        self.assertIsNotNone(result)

    # ---------------------------------------------------------------------
    # ✅ TEST: update_venta
    # ---------------------------------------------------------------------
    def test_update_venta_ok(self):
        """Debe actualizar correctamente los datos de la venta"""
        venta_in = MagicMock()
        venta_in.dict.return_value = {"cantidad": 20, "valorTotal": 20000}

        updated = crud.update_venta(self.mock_db, self.mock_venta, venta_in)

        self.assertEqual(updated, self.mock_venta)
        self.mock_db.commit.assert_called_once()
        self.mock_db.refresh.assert_called_once_with(self.mock_venta)

    # ---------------------------------------------------------------------
    # ✅ TEST: delete_venta
    # ---------------------------------------------------------------------
    def test_delete_venta_ok(self):
        """Debe eliminar la venta correctamente"""
        crud.delete_venta(self.mock_db, self.mock_venta)
        self.mock_db.delete.assert_called_once_with(self.mock_venta)
        self.mock_db.commit.assert_called_once()

    # ---------------------------------------------------------------------
    # ✅ TEST: init_db
    # ---------------------------------------------------------------------
    @patch("app.services.crud.engine")
    @patch("app.services.crud.Base.metadata.create_all")
    def test_init_db_crea_tablas(self, mock_create_all, mock_engine):
        """Debe crear las tablas sin errores"""
        crud.init_db()
        mock_create_all.assert_called_once_with(bind=mock_engine)

    @patch("app.services.crud.Base.metadata.create_all", side_effect=Exception("DB error"))
    def test_init_db_error(self, mock_create_all):
        """Debe lanzar excepción si ocurre error en la creación"""
        with self.assertRaises(Exception):
            crud.init_db()

 