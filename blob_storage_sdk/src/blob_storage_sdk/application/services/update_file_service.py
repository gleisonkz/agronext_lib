from typing import Optional

from ..dtos import File
from ..interfaces import BlobRepository


async def update_file_service(
    blob_repository: BlobRepository,
    document_id: str,
    file: Optional[File] = None,
    metadata: Optional[dict] = None,
) -> bool:
    return await blob_repository.update(
        document_id,
        await file.read() if file else None,
        getattr(file, 'content_type', None),
        metadata,
    )
