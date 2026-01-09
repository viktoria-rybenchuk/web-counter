class WebCounter:
    def __init__(self, storage):
        self.storage = storage

    async def increment_count(self) -> int:
        return await self.storage.increment()

    async def get_count(self) -> int:
        return await self.storage.read()

    async def reset(self) -> None:
        await self.storage.write(0)
