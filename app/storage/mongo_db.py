from typing import Optional

from pymongo import AsyncMongoClient, ReturnDocument


class MongoStorage:
    def __init__(
        self,
        connection_string: str = 'mongodb://localhost:27017',
        database: str = 'test',
        collection: str = 'counter',
    ):
        self.connection_string = connection_string
        self.database_name = database
        self.collection_name = collection
        self.client: Optional[AsyncMongoClient] = None
        self.db = None
        self.collection = None

    async def connect(self):
        if self.client is None:
            self.client = AsyncMongoClient(self.connection_string)
            self.db = self.client.get_database(self.database_name)
            self.collection = self.db.get_collection(self.collection_name)
            await self._init_collection()

    async def _init_collection(self):
        existing = await self.collection.find_one({"id": 1})
        if not existing:
            await self.collection.insert_one({"id": 1, "value": 0})

    async def read(self) -> int:
        if self.client is None:
            await self.connect()

        doc = await self.collection.find_one({"id": 1})
        return doc["value"] if doc else 0

    async def write(self, value: int) -> None:
        if self.client is None:
            await self.connect()

        await self.collection.update_one(
            {"id": 1}, {"$set": {"value": value}}, upsert=True
        )

    async def increment(self) -> int:
        if self.client is None:
            await self.connect()

        doc = await self.collection.find_one_and_update(
            {"id": 1},
            {"$inc": {"value": 1}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        return doc["value"]

    async def close(self):
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            self.collection = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
