from ..interfaces import BlobRepository


async def list_files_service(
    blob_repository: BlobRepository,
) -> list[str]:
    return await blob_repository.list()
