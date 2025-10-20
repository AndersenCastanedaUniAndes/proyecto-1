from __future__ import annotations

from .infrastructure.memory_repo import InMemoryProductoRepo, InMemoryUnitOfWork
from .infrastructure.seed import seed_items
from .infrastructure.postgres import build_uow_from_env


# Contenedor DI. Si hay una URL de base de datos presente, use Postgres; de lo contrario, en memoria.
_pg_uow = build_uow_from_env()
if _pg_uow is not None:
	uow = _pg_uow
else:
	repo = InMemoryProductoRepo(items=seed_items())
	uow = InMemoryUnitOfWork(repo=repo)
