from typing import Optional, Protocol

from pydantic import BaseModel


class File(Protocol):
    filename: str
    content_type: str
    async def read(self) -> bytes: ...


class UploadFileResponse(BaseModel):
    name: str
    url: str


class ListFilesResponse(BaseModel):
    files: list[dict]


class DownloadFileResponse(BaseModel):
    data: Optional[bytes]
    content_type: Optional[str]


class GetFileResponse(BaseModel):
    data: Optional[dict]


class DeleteFileResponse(BaseModel):
    success: bool


class UpdateFileResponse(BaseModel):
    name: str
    url: str
