"""
Script para generar productos dummy y (opcionalmente) enviarlos por POST al endpoint de inventario.

Uso:
  python scripts/generate_dummy_products.py           # dry-run: imprime los payloads
  python scripts/generate_dummy_products.py --post   # envía los POST al servidor
  python scripts/generate_dummy_products.py --count 500 --url http://127.0.0.1:8000/inventario/productos --post

Requiere: httpx (ya incluido en requirements.txt)
"""

from __future__ import annotations
import argparse
import random
import string
import time
from typing import List, Dict, Any
import httpx

DEFAULT_URL = "http://127.0.0.1:8000/inventario/productos"

BASE_NAMES = [
    "Paracetamol", "Ibuprofeno", "Amoxicilina", "Omeprazol", "Metformina",
    "Aspirina", "Cetirizina", "Loratadina", "Diclofenaco", "Naproxeno",
    "Captopril", "Enalapril", "Simvastatina", "Atorvastatina", "Fluconazol",
]
FORMS = ["tabletas", "capsulas", "jarabe", "solucion", "polvo"]
CATEGORIES = ["Analgésicos", "Antibióticos", "Antiinflamatorios", "Antihipertensivos", "Antidiabeticos", "Antialergicos", "Gastrointestinales"]
PROVIDERS = [
    "Laboratorios Pharma Plus", "SaludGen S.A.", "BioMedica Ltda.", "Cuidado Salud S.A.", "Distribuciones Medicas"
]


def random_sku(prefix: str | None = None) -> str:
    if not prefix:
        prefix = ''.join(random.choices(string.ascii_uppercase, k=3))
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}-{suffix}"


def random_lote() -> str:
    year = time.localtime().tm_year
    letters = ''.join(random.choices(string.ascii_uppercase, k=2))
    digits = random.randint(1000, 9999)
    return f"{letters}{year}{digits:04d}"


def random_valor_unitario() -> float:
    # price between 0.05 and 50.00, two decimals
    return round(random.uniform(0.05, 50.0), 2)


def random_bodegas() -> List[Dict[str, Any]]:
    # Two bodegas with random quantities
    b1_qty = random.randint(0, 1000)
    b2_qty = random.randint(0, 1000)
    return [
        {"id": 1, "nombre": "Bodega Principal", "cantidadDisponible": b1_qty, "pasillo": random.choice(list("ABCDE")), "estante": f"A-{random.randint(1,60):02d}"},
        {"id": 2, "nombre": "Bodega Norte", "cantidadDisponible": b2_qty, "pasillo": random.choice(list("ABCDE")), "estante": f"B-{random.randint(1,60):02d}"}
    ]


def build_product(i: int) -> Dict[str, Any]:
    base = random.choice(BASE_NAMES)
    form = random.choice(FORMS)
    strength = random.choice(["100mg", "250mg", "500mg", "5mg/mL", "10mg"])
    nombre = f"{base} {strength} {form} #{i}"
    lote = random_lote()
    sku = random_sku(prefix=(base[:3].upper() if base else None))
    stock_min = random.randint(10, 500)
    proveedor = random.choice(PROVIDERS)
    categoria = random.choice(CATEGORIES)
    valor = random_valor_unitario()
    bodegas = random_bodegas()

    payload = {
        "nombre": nombre,
        "lote": lote,
        "sku": sku,
        "stockMinimo": stock_min,
        "proveedor": proveedor,
        "categoria": categoria,
        "valorUnitario": valor,
        "bodegas": bodegas,
    }
    return payload


def send_product(client: httpx.Client, url: str, product: Dict[str, Any], timeout: float = 10.0) -> httpx.Response:
    return client.post(url, json=product, timeout=timeout)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generador de productos dummy para inventario")
    parser.add_argument("--count", type=int, default=200, help="Número de productos a generar (default: 200)")
    parser.add_argument("--url", type=str, default=DEFAULT_URL, help=f"URL del endpoint (default: {DEFAULT_URL})")
    parser.add_argument("--post", action="store_true", help="Enviar los productos con POST en lugar de dry-run (por defecto dry-run)")
    parser.add_argument("--sleep", type=float, default=0.02, help="Segundos a esperar entre requests cuando --post (default: 0.02)")
    args = parser.parse_args()

    count = args.count
    url = args.url
    do_post = args.post

    print(f"Generando {count} productos. POST mode: {do_post}. URL: {url}\n")

    if do_post:
        client = httpx.Client()
    else:
        client = None

    successes = 0
    failures = 0

    try:
        for i in range(1, count + 1):
            prod = build_product(i)
            if not do_post:
                # dry-run: print compact JSON-like line
                print(f"[{i}/{count}] {prod['nombre']} sku={prod['sku']} stockMin={prod['stockMinimo']} valor={prod['valorUnitario']}")
            else:
                try:
                    resp = send_product(client, url, prod)
                    if resp.status_code in (200, 201):
                        successes += 1
                        print(f"[{i}/{count}] OK {resp.status_code} - {prod['sku']}")
                    else:
                        failures += 1
                        print(f"[{i}/{count}] FAIL {resp.status_code} - {resp.text[:200]}")
                except Exception as exc:
                    failures += 1
                    print(f"[{i}/{count}] EXC: {exc}")
                time.sleep(args.sleep)

    finally:
        if client:
            client.close()

    if do_post:
        print(f"\nEnvío completado. success={successes}, failures={failures}")
    else:
        print(f"\nDry-run completado. Generados={count}")


if __name__ == '__main__':
    main()
