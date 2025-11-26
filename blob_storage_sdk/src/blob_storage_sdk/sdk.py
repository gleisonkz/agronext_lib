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
    ) -> UploadFileResponse:
        url = await save_file_service(self.blob_repository, file)
        return UploadFileResponse(name=file.filename, url=url)

    async def list(self) -> ListFilesResponse:
        urls = await list_files_service(self.blob_repository)
        return ListFilesResponse(urls=urls)

    async def download(self, name: str) -> DownloadFileResponse:
        stream, content_type = await download_file_service(self.blob_repository, name)
        data = b''.join([chunk async for chunk in stream]) if stream else None
        return DownloadFileResponse(data=data, content_type=content_type)

    async def get(self, name: str) -> GetFileResponse:
        data = await get_file_service(self.blob_repository, name)
        return GetFileResponse(data=data)

    async def update(
        self,
        name: str,
        file: File,
    ) -> UpdateFileResponse:
        url = await update_file_service(self.blob_repository, name, file)
        return UpdateFileResponse(name=file.filename, url=url)

    async def delete(self, name: str) -> DeleteFileResponse:
        success = await delete_file_service(self.blob_repository, name)
        return DeleteFileResponse(success=success)


def main() -> None:
    '''exemple usage of the BlobStorageSDK'''
    async def run() -> None:
        sdk = BlobStorageSDK()
        class FakeFile:
            filename = 'example.txt'
            content_type = 'text/plain'
            async def read(self) -> bytes:
                return b'Hello, World!'

        list_response: ListFilesResponse = await sdk.list()
        print(f'Files: {list_response.urls}')

        file: File = FakeFile()
        upload_response: UpdateFileResponse = await sdk.upload(file)
        print(f'Uploaded: {upload_response}')

        list_response: ListFilesResponse = await sdk.list()
        print(f'Files: {list_response.urls}')

        filename: str = list_response.urls[0]
        download_response: DownloadFileResponse = await sdk.download(filename)
        print(f'Downloaded data: {download_response.data}')

    import asyncio
    asyncio.run(run())
