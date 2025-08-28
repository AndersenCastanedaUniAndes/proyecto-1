import asyncpg
import os
import logging

pool = None


def _get_db_dsn():
    # DATABASE_URL standard e.g. postgresql://user:pass@host:5432/dbname
    return os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/cqrs_db")


async def init_db():
    """Inicializa el pool de conexiones usando la variable de entorno DATABASE_URL."""
    global pool
    dsn = _get_db_dsn()
    logging.getLogger(__name__).info(f"Inicializando pool a {dsn}")
    pool = await asyncpg.create_pool(dsn=dsn, min_size=1, max_size=10)

async def fetch(sql: str, *args):
    """Ejecuta un SELECT que devuelve varias filas"""
    async with pool.acquire() as conn:
        return await conn.fetch(sql, *args)

async def fetchrow(sql: str, *args):
    """Ejecuta un SELECT o INSERT ... RETURNING que devuelve una sola fila"""
    async with pool.acquire() as conn:
        return await conn.fetchrow(sql, *args)

async def execute(sql: str, *args):
    """Ejecuta un comando (INSERT/UPDATE/DELETE) sin necesidad de retornar filas"""
    async with pool.acquire() as conn:
        return await conn.execute(sql, *args)
