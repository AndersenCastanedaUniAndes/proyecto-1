"""
Inventario microservice package.

Architecture:
- domain: core entities and repository interfaces
- application: CQRS commands/queries and handlers
- infrastructure: repo implementations, unit of work, seed data
- api: FastAPI routers
- schemas: Pydantic I/O models
"""
