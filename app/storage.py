import asyncio
from pathlib import Path

import aiofiles


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


class FileStorage:
    def __init__(self, file_path: str = "counter.txt"):
        self.lock = asyncio.Lock()
        self.file_path = Path(file_path)

    async def read(self) -> int:
        try:
            async with aiofiles.open(self.file_path, mode='r') as f:
                content = await f.read()
                return int(content.strip())
        except FileNotFoundError:
            await self.write(0)
            return 0

    async def write(self, value: int) -> None:
        async with aiofiles.open(self.file_path, mode='w') as f:
            await f.write(str(value))

    async def increment(self) -> int:
        async with self.lock:
            current = await self.read()
            new_value = current + 1
            await self.write(new_value)
            return new_value
