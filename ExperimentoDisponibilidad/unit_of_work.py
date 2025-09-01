from asyncpg import Pool

class UnitOfWork:
    def __init__(self, pool: Pool):
        self.pool = pool

    async def __aenter__(self):
        self.conn = await self.pool.acquire()
        self.transaction = self.conn.transaction()
        await self.transaction.start()

        # await self.conn.execute("SET LOCAL statement_timeout = 5000")  # 5s
        # await self.conn.execute("SET LOCAL lock_timeout = 1000")       # 1s

        return self.conn

    async def __aexit__(self, exc_type, exc, tb):
        if exc:
            await self.transaction.rollback()
        else:
            await self.transaction.commit()
        await self.pool.release(self.conn)
