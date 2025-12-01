from typing import Optional

from ..interfaces import BlobRepository


async def download_file_service(
    blob_repository: BlobRepository,
    document_id: str,
) -> tuple[Optional[bytes], Optional[str]]:
    stream = await blob_repository.download(document_id)
    data = await blob_repository.get(document_id)
    content_type = data.get('content_settings', {}).get('content_type')
    return stream, content_type
