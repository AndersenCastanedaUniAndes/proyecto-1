from datetime import datetime

from ..domain.models import Bodega, ProductoInventario


def seed_items() -> list[ProductoInventario]:
    return [
        ProductoInventario(
            id=1,
            nombre="Paracetamol 500mg",
            lote="PT2024001",
            sku="PAR500-001",
            stock_total=2500,
            stock_minimo=500,
            bodegas=[
                Bodega(id=1, nombre="Bodega Principal", cantidad_disponible=1500, pasillo="A", estante="A-12"),
                Bodega(id=2, nombre="Bodega Norte", cantidad_disponible=1000, pasillo="B", estante="B-08"),
            ],
            fecha_ultima_actualizacion=datetime.fromisoformat("2024-03-15T00:00:00"),
            proveedor="Laboratorios Pharma Plus",
            categoria="Analgésicos",
            valor_unitario=0.25,
        ),
        ProductoInventario(
            id=2,
            nombre="Vacuna COVID-19",
            lote="VC2024001",
            sku="VAC-CV19-001",
            stock_total=45,
            stock_minimo=50,
            bodegas=[
                Bodega(id=3, nombre="Bodega Controlada", cantidad_disponible=45, pasillo="C", estante="C-01"),
            ],
            fecha_ultima_actualizacion=datetime.fromisoformat("2024-03-14T00:00:00"),
            proveedor="Distribuidora Médica Central",
            categoria="Vacunas",
            valor_unitario=15.50,
        ),
        ProductoInventario(
            id=3,
            nombre="Ibuprofeno 600mg",
            lote="IB2024001",
            sku="IBU600-001",
            stock_total=1200,
            stock_minimo=300,
            bodegas=[
                Bodega(id=1, nombre="Bodega Principal", cantidad_disponible=800, pasillo="A", estante="A-15"),
                Bodega(id=4, nombre="Bodega Sur", cantidad_disponible=400, pasillo="D", estante="D-05"),
            ],
            fecha_ultima_actualizacion=datetime.fromisoformat("2024-03-13T00:00:00"),
            proveedor="Laboratorios Pharma Plus",
            categoria="Antiinflamatorios",
            valor_unitario=0.35,
        ),
        ProductoInventario(
            id=4,
            nombre="Insulina Rápida",
            lote="IN2024001",
            sku="INS-RAP-001",
            stock_total=0,
            stock_minimo=20,
            bodegas=[],
            fecha_ultima_actualizacion=datetime.fromisoformat("2024-03-10T00:00:00"),
            proveedor="Distribuidora Médica Central",
            categoria="Hormonas",
            valor_unitario=25.00,
        ),
        ProductoInventario(
            id=5,
            nombre="Amoxicilina 875mg",
            lote="AM2024001",
            sku="AMX875-001",
            stock_total=35,
            stock_minimo=100,
            bodegas=[
                Bodega(id=2, nombre="Bodega Norte", cantidad_disponible=35, pasillo="B", estante="B-12"),
            ],
            fecha_ultima_actualizacion=datetime.fromisoformat("2024-03-12T00:00:00"),
            proveedor="Farmacéutica del Valle",
            categoria="Antibióticos",
            valor_unitario=0.65,
        ),
    ]
