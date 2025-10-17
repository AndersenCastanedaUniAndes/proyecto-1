from __future__ import annotations

import os

from .infrastructure.memory_repo import InMemoryProductoRepo, InMemoryUnitOfWork
from .infrastructure.seed import seed_items
from .infrastructure.postgres import build_uow_from_env


# Simple manual DI container. If a DB URL is present, use Postgres; otherwise in-memory.
_pg_uow = build_uow_from_env()
if _pg_uow is not None:
	uow = _pg_uow
else:
	repo = InMemoryProductoRepo(items=seed_items())
	uow = InMemoryUnitOfWork(repo=repo)
