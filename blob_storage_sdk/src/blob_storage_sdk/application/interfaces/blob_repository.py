from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional


class BlobRepository(ABC):
    @abstractmethod
    async def upload(
        self,
        name: str,
        data: bytes,
        content_type: str,
        document_id: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> str: ...

    @abstractmethod
    async def list(self, starts_with: Optional[str] = None) -> list[dict]: ...

    @abstractmethod
    async def download(self, document_id: str) -> Optional[AsyncIterator[bytes]]: ...

    @abstractmethod
    async def delete(self, document_id: str) -> bool: ...

    @abstractmethod
    async def get(self, document_id: str) -> Optional[dict]: ...

    @abstractmethod
    async def update(
        self,
        data: bytes,
        content_type: str,
        document_id: str,
        metadata: Optional[dict] = None,
    ) -> str: ...
