from typing import Optional

from ..interfaces import BlobRepository


async def get_file_service(
    blob_repository: BlobRepository,
    document_id: str,
) -> Optional[dict]:
    return await blob_repository.get(document_id)
