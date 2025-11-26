from .application.interfaces import (
    BlobRepository,
)
from .infrastructure import (
    AzureBlobRepository,
)


def get_blob_repository(**kwargs: dict) -> BlobRepository:
    return AzureBlobRepository(**kwargs)
