from ..dtos import File
from ..interfaces import BlobRepository


async def update_file_service(
    blob_repository: BlobRepository,
    file: File,
) -> bool:
    return await blob_repository.update(
        file.filename,
        await file.read(),
        file.content_type,
    )
