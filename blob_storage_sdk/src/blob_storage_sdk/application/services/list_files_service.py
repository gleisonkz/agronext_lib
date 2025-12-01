from typing import Optional

from ..interfaces import BlobRepository


async def list_files_service(
    blob_repository: BlobRepository,
    starts_with: Optional[str] = None,
) -> list[str]:
    return await blob_repository.list(starts_with)
