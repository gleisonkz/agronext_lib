from typing import Optional

from ..dtos import File
from ..interfaces import BlobRepository


async def save_file_service(
    blob_repository: BlobRepository,
    file: File,
    document_id: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> str:
    return await blob_repository.upload(
        file.filename,
        await file.read(),
        file.content_type,
        document_id,
        metadata,
    )
