import os

from app.storage.db_storage import DBStorage
from app.storage.file_storage import FileStorage
from app.storage.in_memory import InMemoryStorage


def get_storage():
    storage_type = os.getenv('STORAGE_TYPE', 'MEMORY')

    if storage_type == 'FILE':
        return FileStorage()
    elif storage_type == 'DB':
        return DBStorage()
    else:
        return InMemoryStorage()
