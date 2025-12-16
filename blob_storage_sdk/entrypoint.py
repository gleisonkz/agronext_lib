import asyncio
from datetime import datetime
from pathlib import Path
from uuid import uuid4
import httpx
from blob_storage_sdk import (
    BlobStorageSDK,
    DownloadFileResponse,
    File,
    ListFilesResponse,
    UpdateFileResponse,
    UploadFileResponse,
)


class FakeFile:
    filename = "example.txt"
    content_type = "text/plain"

    def __len__(self) -> int:
        return 13

    async def read(self) -> bytes:
        return b"Hello, World!"


async def main(sdk) -> None:
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
    upload_date = datetime.now().isoformat()
    metadata = {
        "id": document_id,
        "file_name": name,
        "description": description,
        "document_type": document_type,
        "file_size": str(file_size),
        "upload_date": upload_date,
        "quotation_id": quotation_id,
    }

    signed_url = sdk.writer_signed_url(document_id)
    signed_url.url = "http://ABsDevAgroFeBe:8005/devstoreaccount1/uploads/d7621c8e-8fc6-4f3e-8552-9df541991219.Outro.f7c3ce3e-b44e-442c-b73b-7d8539bb796f?se=2025-12-17T00%3A04%3A21Z&sp=rcw&sv=2025-11-05&sr=b&sig=SdHLSwx1/5F/hjYH0hODxYIx66zJfvr2G3D8GpZpnow%3D"

    list_response: ListFilesResponse = await sdk.list(quotation_id)
    print(f"Files: {list_response.files[0]}")

    filename: str = list_response.files[-1]
    download_response: DownloadFileResponse = await sdk.download(document_id)
    print(f"Downloaded data: {download_response.data}")

    # get_response: ListFilesResponse = await sdk.get(list_response.files[-1]['id'])
    # print('get_response:', get_response.data.metadata)

    updated_response: UpdateFileResponse = await sdk.update(
        document_id, metadata=dict(metadata, updated="True")
    )
    print(f"Updated: {updated_response}")

    get_response: ListFilesResponse = await sdk.get(document_id)
    print("get_response:", get_response.data)


async def upload(sdk, signed_url):
    file: File = FakeFile()
    quotation_id = "12345"
    document_type = "example"
    name = file.filename
    description = "This is an example file."
    _extension = Path(file.filename).suffix
    document_id = f"{quotation_id}.{uuid4()}{_extension}"
    file_size = len(file)
    upload_date = datetime.now().isoformat()
    metadata = {
        "id": document_id,
        "file_name": name,
        "description": description,
        "document_type": document_type,
        "file_size": str(file_size),
        "upload_date": upload_date,
        "quotation_id": quotation_id,
    }

    print(f"Signed URL: {signed_url}")
    async with httpx.AsyncClient() as client:
        upload_response = await client.put(
            signed_url,
            content=await file.read(),
            headers={"x-ms-blob-type": "BlockBlob", "Content-Type": file.content_type},
        )
        upload_response.raise_for_status()
        print(f"Uploaded via signed URL with status: {upload_response.status_code}")

    upload_response: UploadFileResponse = await sdk.upload(file, document_id, metadata)
    print(f"Uploaded: {upload_response}")


if __name__ == "__main__":
    protocol = "http"
    blob_host = "ABsDevAgroFeBe"
    blob_port = 8005
    account_key = "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUY="
    account_name = "devstoreaccount1"
    blob_endpoint = f"http://{blob_host}:{blob_port}/{account_name}"
    conn_string = f"DefaultEndpointsProtocol={protocol};AccountName={account_name};AccountKey={account_key};BlobEndpoint={blob_endpoint}"
    sdk = BlobStorageSDK(connection_string=conn_string)
    # asyncio.run(main(sdk))
    asyncio.run(
        upload(
            sdk,
            signed_url="http://ABsDevAgroFeBe:8005/devstoreaccount1/uploads/d7621c8e-8fc6-4f3e-8552-9df541991219.Outro.f7c3ce3e-b44e-442c-b73b-7d8539bb796f?se=2025-12-17T00%3A04%3A21Z&sp=rcw&sv=2025-11-05&sr=b&sig=SdHLSwx1/5F/hjYH0hODxYIx66zJfvr2G3D8GpZpnow%3D",
        )
    )
