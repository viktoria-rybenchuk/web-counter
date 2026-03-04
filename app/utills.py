import os

from app.storage.cassandra_db import CassandraStorage
from app.storage.mongo_db import MongoStorage
from app.storage.postgres_db import DBStorage
from app.storage.file_storage import FileStorage
from app.storage.hazelcast_db import HZStorage
from app.storage.in_memory import InMemoryStorage


def get_storage():
    storage_type = os.getenv('STORAGE_TYPE', 'MEMORY')

    if storage_type == 'FILE':
        return FileStorage()
    elif storage_type == 'POSTGRES':
        return DBStorage()
    elif storage_type == 'HAZELCAST':
        return HZStorage()
    elif storage_type == 'MONGODB':
        return MongoStorage()
    elif storage_type == 'CASSANDRA':
        return CassandraStorage()
    else:
        return InMemoryStorage()
