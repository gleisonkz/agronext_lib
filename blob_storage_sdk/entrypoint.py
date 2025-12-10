import asyncio
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from blob_storage_sdk import (
    BlobStorageSDK,
    DownloadFileResponse,
    File,
    ListFilesResponse,
    UpdateFileResponse,
    UploadFileResponse,
)


async def main() -> None:
    account_key = "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUY="
    account_name = "devstoreaccount1"
    blob_endpoint = f"http://localhost:10000/{account_name}"
    conn_string = f"DefaultEndpointsProtocol=http;AccountName={account_name};AccountKey={account_key};BlobEndpoint={blob_endpoint}"
    sdk = BlobStorageSDK(connection_string=conn_string)

    class FakeFile:
        filename = "example.txt"
        content_type = "text/plain"

        def __len__(self) -> int:
            return 13

        async def read(self) -> bytes:
            return b"Hello, World!"

    list_response: ListFilesResponse = await sdk.list()
    print(f"Files: {list_response.files[0]}")

    file: File = FakeFile()
    quotation_id = "12345"
    document_type = "example"
    name = file.filename
    description = "This is an example file."
    _extension = Path(file.filename).suffix
    document_id = f"{quotation_id}.{uuid4()}{_extension}"
    file_size = len(file)
    upload_date = datetime.utcnow().isoformat()
    metadata = {
        "id": document_id,
        "file_name": name,
        "description": description,
        "document_type": document_type,
        "file_size": str(file_size),
        "upload_date": upload_date,
        "quotation_id": quotation_id,
    }
    upload_response: UploadFileResponse = await sdk.upload(file, document_id, metadata)
    print(f"Uploaded: {upload_response}")

    list_response: ListFilesResponse = await sdk.list(quotation_id)
    print(f"Files: {list_response.files[0]}")

    filename: str = list_response.files[-1]
    download_response: DownloadFileResponse = await sdk.download(document_id)
    print(f"Downloaded data: {download_response.data}")

    # get_response: ListFilesResponse = await sdk.get(list_response.files[-1]['id'])
    # print('get_response:', get_response.data.metadata)

    updated_response: UpdateFileResponse = await sdk.update(document_id, metadata=dict(metadata, updated="True"))
    print(f"Updated: {updated_response}")

    get_response: ListFilesResponse = await sdk.get(document_id)
    print("get_response:", get_response.data)


if __name__ == "__main__":
    asyncio.run(main())
