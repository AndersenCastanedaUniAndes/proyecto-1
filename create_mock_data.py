import string
import random
import httpx
import asyncio

proveedores = [
    {
        "nombre": "Proveedor A",
        "correoElectronico": "proveedorA@example.com",
        "estado": "Activo",
    },
    {
        "nombre": "Proveedor B",
        "correoElectronico": "proveedorB@example.com",
        "estado": "Activo",
    },
    {
        "nombre": "Proveedor C",
        "correoElectronico": "proveedorC@example.com",
        "estado": "Activo",
    },
    {
        "nombre": "Proveedor D",
        "correoElectronico": "proveedorD@example.com",
        "estado": "Activo",
    },
    {
        "nombre": "Proveedor E",
        "correoElectronico": "proveedorE@example.com",
        "estado": "Activo",
    },
    {
        "nombre": "Proveedor D",
        "correoElectronico": "proveedorD@example.com",
        "estado": "Inactivo",
    },
    {
        "nombre": "Proveedor F",
        "correoElectronico": "proveedorF@example.com",
        "estado": "Inactivo",
    },
    {
        "nombre": "Proveedor G",
        "correoElectronico": "proveedorG@example.com",
        "estado": "Inactivo",
    },
]

productos = [
    {
        "nombre": "Producto AA",
        "lote": "2023A",
        "numeroSerial": "SN2023A",
        "proveedor": "Proveedor A",
        "precioUnidad": 2500,
        "precioTotal": 500000,
        "paisOrigen": "Colombia",
        "uom": "paquete",
        "cantidad": 200,
        "tipoAlmacenamiento": "ambiente",
    },
    {
        "nombre": "Producto AB",
        "lote": "2023A",
        "numeroSerial": "SN2023A",
        "proveedor": "Proveedor A",
        "precioUnidad": 2300,
        "precioTotal": 46000,
        "paisOrigen": "Colombia",
        "uom": "caja",
        "cantidad": 20,
        "tipoAlmacenamiento": "ambiente",
    },
    {
        "nombre": "Producto AC",
        "lote": "2023A",
        "numeroSerial": "SN2023A",
        "proveedor": "Proveedor A",
        "precioUnidad": 1800,
        "precioTotal": 72000,
        "paisOrigen": "Colombia",
        "uom": "pallet",
        "cantidad": 40,
        "tipoAlmacenamiento": "ambiente",
    },
    {
        "nombre": "Producto AD",
        "lote": "2023A",
        "numeroSerial": "SN2023B",
        "proveedor": "Proveedor A",
        "precioUnidad": 2500,
        "precioTotal": 50000,
        "paisOrigen": "Colombia",
        "uom": "paquete",
        "cantidad": 20,
        "tipoAlmacenamiento": "ambiente",
    },
    {
        "nombre": "Producto AE",
        "lote": "2023A",
        "numeroSerial": "SN2023B",
        "proveedor": "Proveedor A",
        "precioUnidad": 2300,
        "precioTotal": 46000,
        "paisOrigen": "Colombia",
        "uom": "caja",
        "cantidad": 20,
        "tipoAlmacenamiento": "ambiente",
    },
    {
        "nombre": "Producto AF",
        "lote": "2023A",
        "numeroSerial": "SN2023B",
        "proveedor": "Proveedor A",
        "precioUnidad": 1800,
        "precioTotal": 72000,
        "paisOrigen": "Colombia",
        "uom": "pallet",
        "cantidad": 40,
        "tipoAlmacenamiento": "ambiente",
    },
]

async def crear_usuarios():
    users = [
        {
            "nombre_usuario": "admin uno",
            "email": "adminuno@email.com",
            "contrasena": "Password123!",
            "rol": "admin"
        },
        {
            "nombre_usuario": "vendedor uno",
            "email": "vendedoruno@email.com",
            "contrasena": "Password123!",
            "rol": "vendedor"
        }
    ]
    clientes = [
        {
            "empresa": "Farmacia Sur",
            "nombre_usuario": "Andersen Castañeda",
            "email": "andersen@farmaciasur.com",
            "contrasena": "Password123!",
            "telefono": "1234567890",
            "direccion": "Calle 123 #45-67",
            "ciudad": "Medellín",
        },
        {
            "empresa": "Farmacia Norte",
            "nombre_usuario": "Damian Cardenas",
            "email": "damian@farmacianorte.com",
            "contrasena": "Password123!",
            "telefono": "1234567890",
            "direccion": "Calle 321 #45-67",
            "ciudad": "Medellín",
        },
    ]

    async with httpx.AsyncClient() as client:
        # for user in users:
        #     response = await client.post("http://localhost:8001/users/", headers={"Content-Type": "application/json"}, json=user)
        #     print (f"Creado: {response.json()}")
        # for cliente in clientes:
        #     response = await client.post("http://localhost:8001/clients", headers={"Content-Type": "application/json"}, json=cliente)
        #     print (f"Creado: {response.json()}")

        clientes_actuales = await client.get("http://localhost:8001/clients", headers={"Content-Type": "application/json"})
        cliente_list = clientes_actuales.json()
        print("Clientes actuales:", cliente_list)
        for c in cliente_list:
            response = await client.post(f"http://localhost:8001/vendedor/2/cliente", headers={"Content-Type": "application/json"}, json={"client_id": c['id']})
            print (f"Asignado: {response.json()}")


async def crear_proveedores():
    url = "http://localhost:8002/proveedores/"

    async with httpx.AsyncClient() as client:
        for proveedor in proveedores:
            response = await client.post(url, headers={"Content-Type": "application/json"}, json=proveedor)
            print (f"Creado: {response.json()}")

async def crear_productos():
    url = "http://localhost:8003/productos/"

    async with httpx.AsyncClient() as client:
        for proveedor in proveedores:
            for producto in productos:
                producto["proveedor"] = proveedor["nombre"]
                producto['nombre'] = "Producto " + producto['nombre'][-2:] + proveedor['nombre'][-1]
                producto['numeroSerial'] = "SN" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                response = await client.post(url, headers={"Content-Type": "application/json"}, json=producto)
                print (f"Creado: {response.json()}")

async def crear_ventas():
    venta1 = {
        "fecha": "2025-11-21 10:30 AM",
        "vendedor": "vendedor uno",
        "vendedor_id": 2,
        "producto": "Producto AAA",
        "producto_id": 1,
        "cantidad": 20,
        "valor_unitario": 2500,
        "valor_total": 50000,
        "cliente": "Farmacia Sur",
        "comision": 2500
    }

    venta2 = {
        "fecha": "2025-11-22 10:30 AM",
        "vendedor": "vendedor uno",
        "vendedor_id": 2,
        "producto": "Producto AB",
        "producto_id": 2,
        "cantidad": 10,
        "valor_unitario": 2300,
        "valor_total": 23000,
        "cliente": "Farmacia Sur",
        "comision": 1150
    }

    url = "http://localhost:8004/ventas/"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers={"Content-Type": "application/json"}, json=venta1)
        print (f"Creado: {response.json()}")
        # response = await client.post(url, headers={"Content-Type": "application/json"}, json=venta2)
        # print (f"Creado: {response.json()}")

async def crear_visitas():
    visita1 = {
        "cliente": "Farmacia Sur",
        "cliente_id": 1,
        "fecha": "2024-01-15",
        "hora": "10:00",
        "direccion": "Calle 123 #45-67",
        "telefono": "1234567890",
        "hallazgos": "Buen estado general.",
        "sugerencias": "Mantener inventario actualizado."
    }

    visita2 = {
        "cliente": "Farmacia Norte",
        "cliente_id": 2,
        "fecha": "2024-01-16",
        "hora": "14:00",
        "direccion": "Calle 321 #45-67",
        "telefono": "0987654321",
        "hallazgos": "Falta de algunos productos.",
        "sugerencias": "Revisar stock semanalmente."
    }

    url = "http://localhost:8004/ventas/visitas"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers={"Content-Type": "application/json"}, json=visita1)
        print (f"Creado: {response.json()}")
        response = await client.post(url, headers={"Content-Type": "application/json"}, json=visita2)
        print (f"Creado: {response.json()}")

async def llenar_inventario():
    async with httpx.AsyncClient() as client:
        produdctos_response = await client.get("http://localhost:8003/productos/", headers={"Content-Type": "application/json"})
        json = produdctos_response.json()
        for producto in json:
            pass
        pass


async def main():
    # await crear_usuarios()
    # await crear_proveedores()
    # await crear_productos()
    # await crear_ventas()
    await llenar_inventario()

asyncio.run(main())
