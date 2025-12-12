from datetime import datetime, timedelta
from unittest.mock import AsyncMock, call, Mock, patch

import pytest

from blob_storage_sdk.azure_blob_client import (
    AzureBlobClient,
)


@pytest.fixture
def fake_container_name() -> str:
    return 'fake_container_name'


@pytest.fixture
def fake_connection_string() -> str:
    return 'fake_connection_string'


@pytest.fixture
def fake_params() -> object:
    class Params:
        name = 'fake_name'
        data = b'fake_bytes'
        content_type = 'image/png'
        document_id = 'abc'
        metadata = {'fake_key': 'fake_value'}
    return Params()


@pytest.fixture
@patch('blob_storage_sdk.azure_blob_client.AsyncBlobServiceClient')
@patch('blob_storage_sdk.azure_blob_client.BlobServiceClient')
def get_azure_blob_client(
    _sync_svc,
    _async_svc,
    fake_container_name,
    fake_connection_string,
) -> AzureBlobClient:
    client = AzureBlobClient(fake_container_name, fake_connection_string)
    client._sync_svc = _sync_svc
    client._async_svc = _async_svc
    return client


def test_init(
    get_azure_blob_client,
    fake_container_name,
    fake_connection_string,
):
    assert get_azure_blob_client.container_name == fake_container_name
    assert get_azure_blob_client.connection_string == fake_connection_string
    get_azure_blob_client._async_svc.from_connection_string.assert_called_once_with(
        conn_str=fake_connection_string,
    )
    assert get_azure_blob_client.client == \
        get_azure_blob_client._async_svc.from_connection_string.return_value
    get_azure_blob_client.client.get_container_client.assert_called_once_with(
        fake_container_name,
    )
    assert get_azure_blob_client.container == \
        get_azure_blob_client.client.get_container_client.return_value


@patch('blob_storage_sdk.azure_blob_client.logger')
@patch('blob_storage_sdk.azure_blob_client.AsyncBlobServiceClient')
@patch('blob_storage_sdk.azure_blob_client.BlobServiceClient')
def test_init_without_connection_string(
    _sync_svc,
    _async_svc,
    mocked_logger,
    fake_container_name,
):
    error_msg = f'Error creating BlobServiceClient with connection string: ...'
    with pytest.raises(Exception) as error:
        AzureBlobClient(fake_container_name, '')
        mocked_logger.error.assert_called_once_with(error_msg)
        assert str(error) == error_msg


@patch('blob_storage_sdk.azure_blob_client.AzureBlobClient._ensure_container_existence')
@patch('blob_storage_sdk.azure_blob_client.AsyncBlobServiceClient')
@patch('blob_storage_sdk.azure_blob_client.BlobServiceClient')
def test_init_calls_ensure_container_existence(
    _sync_svc,
    _async_svc,
    mocked_ensure_container_existence,
    fake_container_name,
    fake_connection_string,
) -> AzureBlobClient:
    AzureBlobClient(fake_container_name, fake_connection_string)
    mocked_ensure_container_existence.assert_called_once_with()


@pytest.mark.asyncio
@patch('blob_storage_sdk.azure_blob_client.logger')
@patch('blob_storage_sdk.azure_blob_client.BlobServiceClient')
async def test_ensure_container_existence(
    _sync_svc,
    mocked_logger,
    get_azure_blob_client,
    fake_container_name,
    fake_connection_string,
):
    response = get_azure_blob_client._ensure_container_existence()
    assert response is None
    _sync_svc.from_connection_string.assert_called_once_with(
        conn_str=fake_connection_string,
    )
    sync_client = _sync_svc.from_connection_string.return_value
    sync_client.get_container_client.assert_called_once_with(fake_container_name)
    sync_container = sync_client.get_container_client.return_value
    sync_container.exists.assert_called_once_with()
    assert not sync_container.create_container.called
    sync_container.close.assert_called_once_with()
    sync_client.close.assert_called_once_with()
    mocked_logger.info.assert_has_calls(
        [
            call('Trying to create container...'),
            call('Container already exists.'),
            call('Container closed.'),
            call('Client closed.'),
        ],
        any_order=False,
    )


@patch('blob_storage_sdk.azure_blob_client.logger')
@patch('blob_storage_sdk.azure_blob_client.BlobServiceClient')
def test_ensure_container_existence_when_container_dont_exists(
    _sync_svc,
    mocked_logger,
    get_azure_blob_client,
):
    sync_client = _sync_svc.from_connection_string.return_value
    sync_container = sync_client.get_container_client.return_value
    sync_container.exists.return_value = False
    get_azure_blob_client._ensure_container_existence()

    sync_container.exists.assert_called_once_with()
    sync_container.create_container.assert_called_once_with()
    mocked_logger.info.assert_has_calls(
        [
            call('Trying to create container...'),
            call('Container created.'),
            call('Container closed.'),
            call('Client closed.'),
        ],
        any_order=False,
    )


@patch('blob_storage_sdk.azure_blob_client.BlobSasPermissions')
@patch('blob_storage_sdk.azure_blob_client.datetime')
@patch('blob_storage_sdk.azure_blob_client.generate_blob_sas')
def test_get_shared_access_signature(
    mocked_generate_blob_sas,
    mocked_datetime,
    mocked_BlobSasPermissions,
    get_azure_blob_client,
):
    mocked_datetime.now.return_value = datetime.now()
    expected_document_id = 'abc'
    expected_expires_in_seconds = 123
    response = get_azure_blob_client._get_shared_access_signature(
        expected_document_id,
        expected_expires_in_seconds,
    )

    assert response is mocked_generate_blob_sas.return_value
    mocked_BlobSasPermissions.assert_called_once_with(read=True)
    mocked_generate_blob_sas.assert_called_once_with(
        account_name=get_azure_blob_client.client.account_name,
        account_key=get_azure_blob_client.client.credential.account_key,
        container_name=get_azure_blob_client.container.container_name,
        permission=mocked_BlobSasPermissions.return_value,
        blob_name=expected_document_id,
        expiry=mocked_datetime.now() + timedelta(seconds=expected_expires_in_seconds),
    )


@pytest.mark.asyncio
@patch('blob_storage_sdk.azure_blob_client.ContentSettings')
@patch('blob_storage_sdk.azure_blob_client.AzureBlobClient._get_shared_access_signature')
async def test_upload(
    mocked_get_shared_access_signature,
    mocked_ContentSettings,
    get_azure_blob_client,
    fake_params,
):
    mocked_blob = AsyncMock()
    get_azure_blob_client.container.get_blob_client.return_value = mocked_blob
    response = await get_azure_blob_client.upload(
        fake_params.name,
        fake_params.data,
        fake_params.content_type,
        fake_params.document_id,
        fake_params.metadata,
    )

    assert type(response) is str
    assert response == f'{mocked_blob.url}?{mocked_get_shared_access_signature.return_value}'
    get_azure_blob_client.container.get_blob_client.assert_called_once_with(
        fake_params.document_id,
    )
    mocked_ContentSettings.assert_called_once_with(content_type=fake_params.content_type)
    mocked_blob.upload_blob.assert_called_once_with(
        fake_params.data,
        overwrite=True,
        content_settings=mocked_ContentSettings.return_value,
        metadata=fake_params.metadata,
    )


@pytest.mark.asyncio
@patch('blob_storage_sdk.azure_blob_client.AzureBlobClient._get_shared_access_signature')
@patch('blob_storage_sdk.azure_blob_client.time.time')
async def test_upload_without_document_id(
    mocked_time,
    mocked_get_shared_access_signature,
    get_azure_blob_client,
    fake_params,
):
    expected_document_id = f'{int(mocked_time.return_value)}_{fake_params.name}'
    mocked_blob = AsyncMock()
    get_azure_blob_client.container.get_blob_client.return_value = mocked_blob
    await get_azure_blob_client.upload(
        fake_params.name,
        fake_params.data,
        fake_params.content_type,
    )

    assert fake_params.document_id != expected_document_id
    mocked_get_shared_access_signature.assert_called_once_with(expected_document_id)


@pytest.mark.asyncio
async def test_list(get_azure_blob_client):
    mocked_itens = [Mock(metadata='fake')]
    expected_itens = [item.metadata for item in mocked_itens]
    expected_starts_with = 'fake_starts_with'
    get_azure_blob_client.container.list_blobs.return_value.__aiter__.return_value = mocked_itens
    response = await get_azure_blob_client.list(expected_starts_with)

    assert type(response) is list
    assert response == expected_itens
    get_azure_blob_client.container.list_blobs.assert_called_once_with(
        name_starts_with=expected_starts_with,
        include=['metadata'],
    )


@pytest.mark.asyncio
async def test_download(
    get_azure_blob_client,
    fake_params,
):
    mocked_blob = AsyncMock()
    mocked_blob.download_blob.return_value = Mock()
    get_azure_blob_client.container.get_blob_client.return_value = mocked_blob
    response = await get_azure_blob_client.download(fake_params.document_id)

    assert response is mocked_blob.download_blob.return_value.chunks.return_value
    get_azure_blob_client.container.get_blob_client.assert_called_once_with(
        fake_params.document_id,
    )
    mocked_blob.download_blob.assert_called_once_with()
    mocked_blob.download_blob.return_value.chunks.assert_called_once_with()


@pytest.mark.asyncio
@patch('blob_storage_sdk.azure_blob_client.logger')
async def test_download_exception(
    mocked_logger,
    get_azure_blob_client,
    fake_params,
):
    with pytest.raises(Exception) as error:
        response = await get_azure_blob_client.download(fake_params.document_id)
        assert response is None
        mocked_logger.error.assert_called_once_with(f'{error=}')


@pytest.mark.asyncio
async def test_delete(
    get_azure_blob_client,
    fake_params,
):
    mocked_blob = AsyncMock()
    get_azure_blob_client.container.get_blob_client.return_value = mocked_blob
    response = await get_azure_blob_client.delete(fake_params.document_id)

    assert type(response) is bool
    assert response is True
    get_azure_blob_client.container.get_blob_client.assert_called_once_with(
        fake_params.document_id,
    )
    mocked_blob.delete_blob.assert_called_once_with()


@pytest.mark.asyncio
@patch('blob_storage_sdk.azure_blob_client.logger')
async def test_delete_exception(
    mocked_logger,
    get_azure_blob_client,
    fake_params,
):
    with pytest.raises(Exception) as error:
        response = await get_azure_blob_client.delete(fake_params.document_id)
        assert response is None
        mocked_logger.error.assert_called_once_with(f'{error=}')


@pytest.mark.asyncio
@patch('blob_storage_sdk.azure_blob_client.AzureBlobClient._get_shared_access_signature')
async def test_get(
    mocked_get_shared_access_signature,
    get_azure_blob_client,
    fake_params,
):
    mocked_blob = AsyncMock()
    get_azure_blob_client.container.get_blob_client.return_value = mocked_blob
    response = await get_azure_blob_client.get(fake_params.document_id)

    assert response is mocked_blob.get_blob_properties.return_value
    assert response.url ==\
        f'{mocked_blob.url}?{mocked_get_shared_access_signature.return_value}'
    get_azure_blob_client.container.get_blob_client.assert_called_once_with(
        fake_params.document_id,
    )
    mocked_blob.get_blob_properties.assert_called_once_with()


@pytest.mark.asyncio
@patch('blob_storage_sdk.azure_blob_client.logger')
async def test_get_exception(
    mocked_logger,
    get_azure_blob_client,
    fake_params,
):
    with pytest.raises(Exception) as error:
        response = await get_azure_blob_client.get(fake_params.document_id)
        assert response is None
        mocked_logger.error.assert_called_once_with(f'{error=}')


@pytest.mark.asyncio
@patch('blob_storage_sdk.azure_blob_client.ContentSettings')
@patch('blob_storage_sdk.azure_blob_client.AzureBlobClient._get_shared_access_signature')
async def test_update(
    mocked_get_shared_access_signature,
    mocked_ContentSettings,
    get_azure_blob_client,
    fake_params,
):
    expected_metadata = {'fake_previous_metadata': 'value'}
    mocked_blob = AsyncMock()
    mocked_blob.get_blob_properties.return_value.metadata = expected_metadata
    get_azure_blob_client.container.get_blob_client.return_value = mocked_blob
    response = await get_azure_blob_client.update(
        fake_params.document_id,
        fake_params.data,
        fake_params.content_type,
        fake_params.metadata,
    )

    assert response ==\
        f'{mocked_blob.url}?{mocked_get_shared_access_signature.return_value}'
    get_azure_blob_client.container.get_blob_client.assert_called_once_with(
        fake_params.document_id,
    )
    mocked_blob.get_blob_properties.assert_called_once_with()
    assert not mocked_blob.set_blob_metadata.called
    mocked_blob.upload_blob.assert_called_once_with(
        fake_params.data,
        overwrite=True,
        content_settings=mocked_ContentSettings(content_type=fake_params.content_type),
        metadata={
            **expected_metadata,
            **fake_params.metadata,
        },
    )


@pytest.mark.asyncio
@patch('blob_storage_sdk.azure_blob_client.ContentSettings')
@patch('blob_storage_sdk.azure_blob_client.AzureBlobClient._get_shared_access_signature')
async def test_update_without_content_type(
    _,
    mocked_ContentSettings,
    get_azure_blob_client,
    fake_params,
):
    expected_metadata = {'fake_previous_metadata': 'value'}
    mocked_blob = AsyncMock()
    mocked_blob.get_blob_properties.return_value.metadata = expected_metadata
    get_azure_blob_client.container.get_blob_client.return_value = mocked_blob
    await get_azure_blob_client.update(
        fake_params.document_id,
        fake_params.data,
        None,
        fake_params.metadata,
    )

    mocked_blob.upload_blob.assert_called_once_with(
        fake_params.data,
        overwrite=True,
        content_settings=mocked_ContentSettings(
            content_type=mocked_blob.get_blob_properties.return_value.content_settings.content_type,
        ),
        metadata={
            **expected_metadata,
            **fake_params.metadata,
        },
    )


@pytest.mark.asyncio
@patch('blob_storage_sdk.azure_blob_client.AzureBlobClient._get_shared_access_signature')
async def test_update_without_data(
    mocked_get_shared_access_signature,
    get_azure_blob_client,
    fake_params,
):
    expected_metadata = {'fake_previous_metadata': 'value'}
    mocked_blob = AsyncMock()
    mocked_blob.get_blob_properties.return_value.metadata = expected_metadata
    get_azure_blob_client.container.get_blob_client.return_value = mocked_blob
    response = await get_azure_blob_client.update(
        fake_params.document_id,
        None,
        None,
        fake_params.metadata,
    )

    assert response ==\
        f'{mocked_blob.url}?{mocked_get_shared_access_signature.return_value}'
    assert not mocked_blob.upload_blob.called
    mocked_blob.set_blob_metadata.assert_called_once_with({
        **expected_metadata,
        **fake_params.metadata,
    })


@pytest.mark.asyncio
@patch('blob_storage_sdk.azure_blob_client.logger')
async def test_update_exception(
    mocked_logger,
    get_azure_blob_client,
    fake_params,
):
    with pytest.raises(Exception) as _error:
        await get_azure_blob_client.update(fake_params.document_id)
    error = _error.value
    mocked_logger.error.assert_called_once_with(f'{error=}')
    assert isinstance(error, Exception)
    assert not isinstance(error, FileNotFoundError)


@pytest.mark.asyncio
async def test_update_file_not_found(
    get_azure_blob_client,
    fake_params,
):
    client = get_azure_blob_client._async_svc.from_connection_string.return_value
    container = client.get_container_client.return_value
    blob = container.get_blob_client.return_value
    blob.exists = AsyncMock(return_value=False)
    with pytest.raises(FileNotFoundError) as error:
        await get_azure_blob_client.update(fake_params.document_id)
    assert isinstance(error.value, FileNotFoundError)
    assert str(error.value) == f"File '{fake_params.document_id}' not found."
