# Inventario Microservicio

Microservicio de Inventario en FastAPI con Clean Architecture y CQRS.

## Estructura
- app/domain: Entidades y repositorios
- app/application: CQRS (commands/queries/handlers)
- app/infrastructure: Implementaciones (memoria) y seed
- app/api: Rutas FastAPI
- app/schemas: Modelos Pydantic para I/O

## Ejecutar local

1. Crear y activar un ambiente virtual (opcional pero recomendado)
2. Instalar dependencias
3. Ejecutar servidor

## Usar PostgreSQL

Por defecto el servicio usa un repositorio en memoria con datos de ejemplo. Para usar PostgreSQL:

1. Levanta una base de datos local con Docker:
	docker compose up -d postgres

2. Crear ambiente y activarlo

3. Instala dependencias de base de datos y ejecuta la app:
	pip install -r requirements.txt
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Endpoints:
- GET /healthz
- GET /inventario/productos?q=term
- GET /inventario/productos/{id}
- POST /inventario/productos { CrearProductoRequest }
- POST /inventario/productos/{id}/ajustar { bodegaId, delta }
