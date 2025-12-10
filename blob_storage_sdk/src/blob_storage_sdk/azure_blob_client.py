import logging
import time
from datetime import datetime, timedelta
from typing import AsyncIterator, Optional

from azure.storage.blob import (
    BlobSasPermissions,
    BlobServiceClient,
    ContentSettings,
    generate_blob_sas,
)
from azure.storage.blob.aio import BlobServiceClient as AsyncBlobServiceClient


logger = logging.getLogger('infrastructure.azure_blob_client')


class AzureBlobClient:
    def __init__(
        self,
        container_name: str,
        connection_string: str,
    ) -> None:
        self.container_name = container_name
        self.connection_string = connection_string
        if not self.connection_string:
            raise Exception('Missing required conn string to connect blob storage')

        try:
            self.client = AsyncBlobServiceClient.from_connection_string(
                conn_str=self.connection_string,
            )

        except Exception as _:
            error_msg = f'Error creating BlobServiceClient with connection string: {self.connection_string[:10]}...'
            logger.error(error_msg)
            raise Exception(error_msg)

        self.container = self.client.get_container_client(self.container_name)
        self._ensure_container_existence()

    def _ensure_container_existence(self) -> None:
        sync_client = BlobServiceClient.from_connection_string(
            conn_str=self.connection_string,
        )
        sync_container = sync_client.get_container_client(self.container_name)

        logger.info('Trying to create container...')
        if sync_container.exists():
            logger.info('Container already exists.')

        else:
            logger.info('Container created.')
            sync_container.create_container()

        sync_container.close()
        sync_client.close()
        logger.info('Container closed.')
        logger.info('Client closed.')

    def _get_shared_access_signature(
        self,
        document_id: str,
        expires_in_seconds: int=3600,
    ) -> str:
        return generate_blob_sas(
            account_name=self.client.account_name,
            account_key=self.client.credential.account_key,
            container_name=self.container.container_name,
            permission=BlobSasPermissions(read=True),
            blob_name=document_id,
            expiry=datetime.now() + timedelta(seconds=expires_in_seconds),
        )

    async def upload(
        self,
        name: str,
        data: bytes,
        content_type: str,
        document_id: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> str:
        if not document_id:
            timestamp = int(time.time())
            document_id = f'{timestamp}_{name}'
        blob = self.container.get_blob_client(document_id)
        await blob.upload_blob(
            data,
            overwrite=True,
            content_settings=ContentSettings(content_type=content_type),
            metadata=metadata,
        )
        return f'{blob.url}?{self._get_shared_access_signature(document_id)}'

    async def list(self, starts_with: Optional[str] = None) -> list[dict]:
        blobs = []
        async for blob in self.container.list_blobs(
            name_starts_with=starts_with,
            include=['metadata'],
        ):
            blobs.append(blob.metadata)
        return blobs

    async def download(self, document_id: str) -> Optional[AsyncIterator[bytes]]:
        blob = self.container.get_blob_client(document_id)
        try:
            stream = await blob.download_blob()
            return stream.chunks()

        except Exception as error:
            logger.error(f'{error=}')
            return None

    async def delete(self, document_id: str) -> bool:
        blob = self.container.get_blob_client(document_id)
        try:
            await blob.delete_blob()
            return True

        except Exception as error:
            logger.error(f'{error=}')
            return False

    async def get(self, document_id: str) -> Optional[dict]:
        blob = self.container.get_blob_client(document_id)
        try:
            data = await blob.get_blob_properties()
            data.url = f'{blob.url}?{self._get_shared_access_signature(document_id)}'
            return data

        except Exception as error:
            logger.error(f'{error=}')
            return None

    async def update(
        self,
        document_id: str,
        data: Optional[bytes] = None,
        content_type: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> str:
        '''
        # NOTE:
        # If you dont change the content settings AND serve with media type on API
        # the binary will be updated but downloaded file will stick with old content file
        '''
        # TODO: Check existence before updating (or it will create a new one)

        blob = self.container.get_blob_client(document_id)
        try:
            if not await blob.exists():
                return None

            props = await blob.get_blob_properties()
            new_metadata = {
                **(props.metadata or {}),
                **(metadata or {}),
            }

            if not data:
                await blob.set_blob_metadata(new_metadata)
                return f'{blob.url}?{self._get_shared_access_signature(document_id)}'

            await blob.upload_blob(
                data,
                overwrite=True,
                content_settings=ContentSettings(
                    content_type=content_type or props.content_settings.content_type,
                ),
                metadata=new_metadata,
            )
            return f'{blob.url}?{self._get_shared_access_signature(document_id)}'

        except Exception as error:
            logger.error(f'{error=}')
            raise error
