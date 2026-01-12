from fastapi import FastAPI

from app.utills import get_storage
from app.web_counter import WebCounter

app = FastAPI()


storage = get_storage()
web_counter = WebCounter(storage)


@app.get("/inc")
async def increment_counter():
    return await web_counter.increment_count()


@app.get("/count")
async def get_counter_value():
    return {"count": await web_counter.get_count()}
