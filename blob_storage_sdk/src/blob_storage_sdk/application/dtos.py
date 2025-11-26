from dataclasses import dataclass
from typing import Optional, Protocol


class File(Protocol):
    filename: str
    content_type: str
    async def read(self) -> bytes: ...


@dataclass
class UploadFileResponse:
    name: str
    url: str


@dataclass
class ListFilesResponse:
    urls: list[str]


@dataclass
class DownloadFileResponse:
    data: Optional[bytes]
    content_type: Optional[str]


@dataclass
class GetFileResponse:
    data: Optional[dict]


@dataclass
class DeleteFileResponse:
    success: bool


@dataclass
class UpdateFileResponse:
    name: str
    url: str
