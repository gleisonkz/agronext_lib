from typing import Optional

from ..interfaces import BlobRepository


async def download_file_service(
    blob_repository: BlobRepository,
    name: str,
) -> tuple[Optional[bytes], Optional[str]]:
    stream = await blob_repository.download(name)
    data = await blob_repository.get(name)
    content_type = data.get('content_settings', {}).get('content_type')
    return stream, content_type
