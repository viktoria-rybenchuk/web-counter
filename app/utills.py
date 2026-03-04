import os

from app.storage.cassandra_db import CassandraStorage
from app.storage.mongo_db import MongoStorage
from app.storage.neo4j_db import Neo4jStorage
from app.storage.postgres_db import DBStorage
from app.storage.file_storage import FileStorage
from app.storage.hazelcast_db import HZStorage
from app.storage.in_memory import InMemoryStorage

STORAGE_MAP = {
    'MEMORY': InMemoryStorage,
    'FILE': FileStorage,
    'RELATIONAL': DBStorage,
    'KEY_VALUE': HZStorage,
    'DOCUMENT': MongoStorage,
    'COLUMN': CassandraStorage,
    'GRAPH': Neo4jStorage,
}


def get_storage():
    storage_type = os.getenv('STORAGE_TYPE', 'MEMORY')
    storage_class = STORAGE_MAP.get(storage_type)

    if storage_class is None:
        raise ValueError(
            f"Unknown STORAGE_TYPE: '{storage_type}'. Choose from: {list(STORAGE_MAP)}"
        )

    return storage_class()
