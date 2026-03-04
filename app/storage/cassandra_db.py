import asyncio
from typing import Optional, List

from cassandra.cluster import Cluster, Session


class CassandraStorage:
    def __init__(
        self,
        hosts: List[str] = None,
        port: int = 9042,
        keyspace: str = "counter_keyspace",
        table: str = "counter",
    ):
        self.hosts = hosts or ["127.0.0.1"]
        self.port = port
        self.keyspace = keyspace
        self.table = table
        self.cluster: Optional[Cluster] = None
        self.session: Optional[Session] = None
        self._lock = asyncio.Lock()

    async def connect(self):
        async with self._lock:
            if self.session is not None:
                return

            self.cluster = Cluster(self.hosts, port=self.port)
            self.session = self.cluster.connect()

            self.session.execute(
                f"""
                CREATE KEYSPACE IF NOT EXISTS {self.keyspace}
                WITH REPLICATION = {{'class': 'SimpleStrategy', 'replication_factor': '1'}}
            """
            )
            self.session.set_keyspace(self.keyspace)
            self.session.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {self.table} (
                    id int PRIMARY KEY,
                    value counter
                )
            """
            )
            self.session.execute(
                f"UPDATE {self.table} SET value = value + 0 WHERE id = 1"
            )

    async def read(self) -> int:
        if self.session is None:
            await self.connect()

        result = await asyncio.to_thread(
            self.session.execute, f"SELECT value FROM {self.table} WHERE id = 1"
        )
        return result[0].value if result else 0

    async def increment(self) -> int:
        if self.session is None:
            await self.connect()

        await asyncio.to_thread(
            self.session.execute,
            f"UPDATE {self.table} SET value = value + 1 WHERE id = 1",
        )
        result = await asyncio.to_thread(
            self.session.execute, f"SELECT value FROM {self.table} WHERE id = 1"
        )
        return result[0].value if result else 0

    async def close(self):
        if self.session:
            self.session.shutdown()
            self.session = None
        if self.cluster:
            self.cluster.shutdown()
            self.cluster = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
