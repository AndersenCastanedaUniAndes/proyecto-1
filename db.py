import asyncpg
import asyncio

pool = None

async def init_db():
    global pool
    pool = await asyncpg.create_pool(
        user="postgres",
        password="postgres",
        database="cqrs_db",
        host="localhost",
        port=5432,
        min_size=1,
        max_size=10
    )

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
