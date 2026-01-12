import asyncio


class InMemoryStorage:
    def __init__(self):
        self.lock = asyncio.Lock()
        self._count = 0

    async def read(self) -> int:
        return self._count

    async def write(self, value: int) -> None:
        self._count = value

    async def increment(self) -> int:
        async with self.lock:
            self._count += 1
            return self._count
