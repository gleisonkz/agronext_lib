from agronext_database.repositories.base_repository.base_repository import (
    TortoiseRepository,
)


class BaseService[T: TortoiseRepository, D]:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, repository: T) -> None:
        self.repository = repository

    async def exists(self, /, pk: int) -> bool:
        return await self.repository.query(pk=pk).exists()

    async def get_all(self) -> list[D]:
        records = await self.repository.all()
        return records

    async def get(self, /, pk: int) -> D:
        record = await self.repository.get(pk=pk)
        return record

    async def create(self, /, **kwargs) -> D:
        record = await self.repository.create(**kwargs)
        return record

    async def patch(self, /, pk: int, **kwargs) -> D:
        record = await self.get(pk=pk)
        record = await self.repository.patch(record, **kwargs)
        return record

    async def update(self, /, pk: int, **kwargs) -> D:
        record = await self.get(pk=pk)
        record = await self.repository.update(pk=pk, **kwargs)
        return record

    async def delete(self, /, pk: int) -> None:
        record = self.get(pk=pk)
        await self.repository.delete(record)
