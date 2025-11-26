from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional


class BlobRepository(ABC):
    @abstractmethod
    async def upload(self, name: str, data: bytes, content_type: str) -> str: ...

    @abstractmethod
    async def list(self) -> list[str]: ...

    @abstractmethod
    async def download(self, name: str) -> Optional[AsyncIterator[bytes]]: ...

    @abstractmethod
    async def delete(self, name: str) -> bool: ...

    @abstractmethod
    async def get(self, name: str) -> Optional[dict]: ...

    @abstractmethod
    async def update(self, name: str, data: bytes, content_type: str) -> bool: ...
