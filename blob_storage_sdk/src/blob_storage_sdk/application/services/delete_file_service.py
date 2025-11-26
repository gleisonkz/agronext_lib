from ..interfaces import BlobRepository


async def delete_file_service(
    blob_repository: BlobRepository,
    name: str,
) -> bool:
    return await blob_repository.delete(name)
