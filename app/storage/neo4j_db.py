from typing import Optional

from neo4j import AsyncGraphDatabase, AsyncDriver


class Neo4jStorage:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password"):
        self.uri = uri
        self.user = user
        self.password = password
        self.driver: Optional[AsyncDriver] = None

    async def connect(self):
        if self.driver is None:
            self.driver = AsyncGraphDatabase.driver(
                self.uri, auth=(self.user, self.password)
            )

    async def read(self) -> int:
        if self.driver is None:
            await self.connect()

        async with self.driver.session() as session:
            result = await session.run(
                """
                MATCH (i:Item {name: 'Laptop'})
                RETURN i.likes AS likes
                """
            )
            record = await result.single()
            return record["likes"] if record else 0

    async def increment(self) -> int:
        if self.driver is None:
            await self.connect()

        async with self.driver.session() as session:
            result = await session.execute_write(self._increment_tx)
            return result

    @staticmethod
    async def _increment_tx(tx) -> int:
        result = await tx.run(
            """
            MATCH (i:Item {name: 'Laptop'})
            SET i.likes = coalesce(i.likes, 0) + 1
            RETURN i.likes AS likes
            """
        )
        record = await result.single()
        return record["likes"] if record else 0

    async def close(self):
        if self.driver:
            await self.driver.close()
            self.driver = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
