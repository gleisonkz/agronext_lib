from typing import Optional

from .azure_blob_client import AzureBlobClient
from .schemas import (
    DeleteFileResponse,
    DownloadFileResponse,
    File,
    GetFileResponse,
    ListFilesResponse,
    UpdateFileResponse,
    UploadFileResponse,
)


class BlobStorageSDK:
    def __init__(
        self,
        container_name: str = 'uploads',
        connection_string: str = '''
            DefaultEndpointsProtocol=http;
            AccountName=devstoreaccount1;
            AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUY=;
            BlobEndpoint=http://localhost:10000/devstoreaccount1;
        ''',
    ):
        self.container_name = container_name
        self.connection_string = self._format_connection_string(connection_string)
        self.blob_client = AzureBlobClient(
            container_name=self.container_name,
            connection_string=self.connection_string,
        )

    def _format_connection_string(self, connection_string: str) -> str:
        return connection_string.strip().replace('\n', '').replace(' ', '')

    async def upload(
        self,
        file: File,
        document_id: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> UploadFileResponse:
        url = await self.blob_client.upload(
            file.filename,
            await file.read(),
            file.content_type,
            document_id,
            metadata,
        )
        return UploadFileResponse(name=file.filename, url=url)

    async def list(self, starts_with: Optional[str] = None) -> ListFilesResponse:
        files = await self.blob_client.list(starts_with)
        return ListFilesResponse(files=files)

    async def download(self, document_id: str) -> DownloadFileResponse:
        stream = await self.blob_client.download(document_id)
        _data = await self.blob_client.get(document_id)
        content_type = _data.get('content_settings', {}).get('content_type')

        data = b''.join([chunk async for chunk in stream]) if stream else None
        return DownloadFileResponse(data=data, content_type=content_type)

    async def get(self, document_id: str) -> GetFileResponse:
        data = await self.blob_client.get(document_id)
        return GetFileResponse(data=data)

    async def update(
        self,
        document_id: str,
        file: Optional[File] = None,
        metadata: Optional[dict] = None,
    ) -> UpdateFileResponse:
        url = await self.blob_client.update(
            document_id,
            await file.read() if file else None,
            getattr(file, 'content_type', None),
            metadata,
        )
        name = getattr(file, 'filename', None)
        if not name and metadata:
            name = metadata.get('name', document_id)
        return UpdateFileResponse(name=name, url=url)

    async def delete(self, document_id: str) -> DeleteFileResponse:
        success = await self.blob_client.delete(document_id)
        return DeleteFileResponse(success=success)
