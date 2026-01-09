import os

from fastapi import FastAPI

from app.storage import FileStorage, InMemoryStorage
from app.web_counter import WebCounter

app = FastAPI()


storage = FileStorage() if os.getenv('STORAGE_TYPE') == 'FILE' else InMemoryStorage()
web_counter = WebCounter(storage)


@app.get("/inc")
async def increment_counter():
    return await web_counter.increment_count()


@app.get("/count")
async def get_counter_value():
    return {"count": web_counter.get_count()}
