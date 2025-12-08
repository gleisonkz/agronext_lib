from unittest.mock import AsyncMock, patch

import pytest

from blob_storage_sdk import (
    BlobStorageSDK,
    DeleteFileResponse,
    DownloadFileResponse,
    GetFileResponse,
    ListFilesResponse,
    UpdateFileResponse,
    UploadFileResponse,
)


@pytest.fixture
def fake_file():
    class File:
        filename = 'fake.png'
        content_type = 'image/png'
        _read_bytes = b'fake'
        async def read(self) -> bytes:
            return self._read_bytes
    return File()


@pytest.fixture
def fake_metadata() -> dict:
    return {'fake_key': 'fake_value'}


@pytest.fixture
@patch('blob_storage_sdk.sdk.AzureBlobClient', return_value=AsyncMock())
def get_blob_storage(mocked_blob_client, fake_metadata) -> BlobStorageSDK:
    async def _download_result():
        for i in range(2):
            yield b'fake_bytes'
    mocked_blob_client.return_value.upload = AsyncMock(return_value='fake_url')
    mocked_blob_client.return_value.list = AsyncMock(return_value=[fake_metadata])
    mocked_blob_client.return_value.download = AsyncMock(return_value=_download_result())
    mocked_blob_client.return_value.get = AsyncMock(return_value=fake_metadata)
    mocked_blob_client.return_value.update = AsyncMock(return_value='fake_url')
    mocked_blob_client.return_value.delete = AsyncMock(return_value=True)
    sdk = BlobStorageSDK()
    sdk._mocked_blob_client_class = mocked_blob_client
    sdk._mocked_blob_client = mocked_blob_client.return_value
    return sdk


def test_init(get_blob_storage):
    container_name = 'uploads'
    connection_string = 'DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUY=;BlobEndpoint=http://localhost:10000/devstoreaccount1;'
    assert get_blob_storage.container_name == container_name
    assert get_blob_storage.connection_string == connection_string
    get_blob_storage._mocked_blob_client_class.assert_called_once_with(
        container_name=container_name,
        connection_string=connection_string,
    )
    assert get_blob_storage._mocked_blob_client_class.return_value == get_blob_storage._mocked_blob_client


@pytest.mark.asyncio
async def test_upload(get_blob_storage, fake_file, fake_metadata):
    document_id = 'fake_id'
    result = await get_blob_storage.upload(fake_file, document_id, fake_metadata)
    get_blob_storage._mocked_blob_client.upload.assert_called_once_with(
        fake_file.filename,
        fake_file._read_bytes,
        fake_file.content_type,
        document_id,
        fake_metadata,
    )
    assert isinstance(result, UploadFileResponse)
    assert result.name == fake_file.filename
    assert result.url == get_blob_storage._mocked_blob_client.upload.return_value


@pytest.mark.asyncio
async def test_list(get_blob_storage, fake_metadata):
    starts_with = 'fake_relation_id'
    result = await get_blob_storage.list(starts_with)
    get_blob_storage._mocked_blob_client.list.assert_called_once_with(
        starts_with,
    )
    assert isinstance(result, ListFilesResponse)
    assert len(result.files) == 1
    assert result.files == get_blob_storage._mocked_blob_client.list.return_value
    assert result.files[0] == fake_metadata


@pytest.mark.asyncio
async def test_download(get_blob_storage):
    document_id = 'fake_id'
    result_download = await get_blob_storage.download(document_id)
    get_blob_storage._mocked_blob_client.download.assert_called_once_with(
        document_id,
    )
    get_blob_storage._mocked_blob_client.get.assert_called_once_with(
        document_id,
    )
    assert isinstance(result_download, DownloadFileResponse)
    assert result_download.content_type == None
    assert result_download.data == b'fake_bytesfake_bytes'


@pytest.mark.asyncio
async def test_get(get_blob_storage, fake_metadata):
    document_id = 'fake_id'
    result = await get_blob_storage.get(document_id)
    get_blob_storage._mocked_blob_client.get.assert_called_once_with(
        document_id,
    )
    assert isinstance(result, GetFileResponse)
    assert result.data == get_blob_storage._mocked_blob_client.get.return_value
    assert result.data == fake_metadata


@pytest.mark.asyncio
async def test_update(get_blob_storage, fake_file, fake_metadata):
    document_id = 'fake_id'
    result = await get_blob_storage.update(document_id, fake_file, fake_metadata)
    get_blob_storage._mocked_blob_client.update.assert_called_once_with(
        document_id,
        fake_file._read_bytes,
        fake_file.content_type,
        fake_metadata,
    )
    assert isinstance(result, UpdateFileResponse)
    assert result.name == fake_file.filename
    assert result.url == get_blob_storage._mocked_blob_client.update.return_value


@pytest.mark.asyncio
async def test_delete(get_blob_storage):
    document_id = 'fake_id'
    result = await get_blob_storage.delete(document_id)
    get_blob_storage._mocked_blob_client.delete.assert_called_once_with(
        document_id,
    )
    assert isinstance(result, DeleteFileResponse)
    assert result.success == True
    assert result.success == get_blob_storage._mocked_blob_client.delete.return_value
