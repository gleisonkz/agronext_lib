from ..interfaces import BlobRepository


async def delete_file_service(
    blob_repository: BlobRepository,
    document_id: str,
) -> bool:
    return await blob_repository.delete(document_id)
