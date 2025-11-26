from typing import Optional

from ..interfaces import BlobRepository


async def get_file_service(
    blob_repository: BlobRepository,
    name: str,
) -> Optional[dict]:
    return await blob_repository.get(name)
