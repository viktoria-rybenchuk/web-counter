from typing import Optional

import asyncpg


class DBStorage:
    def __init__(
        self,
        host: str = 'localhost',
        port: int = 5432,
        database: str = 'mydatabase',
        user: str = 'myuser',
        password: str = 'mypassword',
        table_name: str = 'counter',
    ):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.table_name = table_name
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        if self.pool is None:
            self.pool = await asyncpg.create_pool(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                min_size=2,
                max_size=20,
                command_timeout=5,
            )
            await self._init_table()

    async def _init_table(self):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {self.table_name} (
                        id INTEGER PRIMARY KEY,
                        value BIGINT NOT NULL DEFAULT 0
                    )
                """
                )

                await conn.execute(
                    f"""
                    INSERT INTO {self.table_name} (id, value)
                    VALUES (1, 0)
                    ON CONFLICT (id) DO NOTHING
                """
                )

    async def read(self) -> int:
        if self.pool is None:
            await self.connect()

        async with self.pool.acquire() as conn:
            async with conn.transaction(isolation='read_committed'):
                value = await conn.fetchval(
                    f"SELECT value FROM {self.table_name} WHERE id = 1"
                )
                return value if value is not None else 0

    async def write(self, value: int) -> None:
        if self.pool is None:
            await self.connect()

        async with self.pool.acquire() as conn:
            async with conn.transaction(isolation='read_committed'):
                await conn.execute(
                    f"UPDATE {self.table_name} SET value = $1 WHERE id = 1", value
                )

    async def increment(self) -> int:
        if self.pool is None:
            await self.connect()

        async with self.pool.acquire() as conn:
            async with conn.transaction(isolation='read_committed'):
                new_value = await conn.fetchval(
                    f"""
                    UPDATE {self.table_name}
                    SET value = value + 1
                    WHERE id = 1
                    RETURNING value
                """
                )
                return new_value

    async def close(self):
        if self.pool:
            await self.pool.close()
            self.pool = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
