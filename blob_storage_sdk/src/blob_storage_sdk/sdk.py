from typing import Optional

from .application.dtos import (
    DeleteFileResponse,
    DownloadFileResponse,
    File,
    GetFileResponse,
    ListFilesResponse,
    UpdateFileResponse,
    UploadFileResponse,
)
from .application.interfaces import BlobRepository
from .application.services import (
    save_file_service,
    list_files_service,
    download_file_service,
    get_file_service,
    update_file_service,
    delete_file_service,
)
from .dependencies import get_blob_repository


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
        self.blob_repository: BlobRepository = get_blob_repository(
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
        url = await save_file_service(self.blob_repository, file, document_id, metadata)
        return UploadFileResponse(name=file.filename, url=url)

    async def list(self, starts_with: Optional[str] = None) -> ListFilesResponse:
        files = await list_files_service(self.blob_repository, starts_with)
        return ListFilesResponse(files=files)

    async def download(self, document_id: str) -> DownloadFileResponse:
        stream, content_type = await download_file_service(self.blob_repository, document_id)
        data = b''.join([chunk async for chunk in stream]) if stream else None
        return DownloadFileResponse(data=data, content_type=content_type)

    async def get(self, document_id: str) -> GetFileResponse:
        data = await get_file_service(self.blob_repository, document_id)
        return GetFileResponse(data=data)

    async def update(
        self,
        document_id: str,
        file: Optional[File] = None,
        metadata: Optional[dict] = None,
    ) -> UpdateFileResponse:
        url = await update_file_service(self.blob_repository, document_id, file, metadata)
        name = getattr(file, 'filename', None)
        if not name and metadata:
            name = metadata.get('name', document_id)
        return UpdateFileResponse(name=name, url=url)

    async def delete(self, document_id: str) -> DeleteFileResponse:
        success = await delete_file_service(self.blob_repository, document_id)
        return DeleteFileResponse(success=success)


def main() -> None:
    '''exemple usage of the BlobStorageSDK'''
    async def run() -> None:
        conn_string = '''
            DefaultEndpointsProtocol=http;
            AccountName=devstoreaccount1;
            AccountKey=Eby8vdM02xNOcqFeqCnb+...==;
            BlobEndpoint=http://absdevagrofebe:10000/devstoreaccount1;
        '''
        sdk = BlobStorageSDK(
            # connection_string=conn_string
        )
        class FakeFile:
            filename = 'example.txt'
            content_type = 'text/plain'
            def __len__(self) -> int: return 13
            async def read(self) -> bytes:
                return b'Hello, World!'

        list_response: ListFilesResponse = await sdk.list()
        print(f'Files: {list_response.files[0]}')

        file: File = FakeFile()
        from datetime import datetime
        quotation_id = '12345'
        document_type = 'example'
        name = file.filename
        description = 'This is an example file.'
        from pathlib import Path
        from uuid import uuid4
        _extension = Path(file.filename).suffix
        document_id = f"{quotation_id}.{uuid4()}{_extension}"
        file_size = len(file)
        upload_date = datetime.utcnow().isoformat()
        metadata = {
            "id": document_id,
            "file_name": name,
            "description": description,
            "document_type": document_type,
            "file_size": str(file_size),
            "upload_date": upload_date,
            "quotation_id": quotation_id,
        }
        upload_response: UploadFileResponse = await sdk.upload(file, document_id, metadata)
        print(f'Uploaded: {upload_response}')

        list_response: ListFilesResponse = await sdk.list(quotation_id)
        print(f'Files: {list_response.files[0]}')

        filename: str = list_response.files[-1]
        download_response: DownloadFileResponse = await sdk.download(document_id)
        print(f'Downloaded data: {download_response.data}')

        # get_response: ListFilesResponse = await sdk.get(list_response.files[-1]['id'])
        # print('get_response:', get_response.data.metadata)

        updated_response: UpdateFileResponse = await sdk.update(document_id, metadata=dict(metadata, updated="True"))
        print(f'Updated: {updated_response}')

        get_response: ListFilesResponse = await sdk.get(document_id)
        print('get_response:', get_response.data.metadata)

    import asyncio
    asyncio.run(run())
