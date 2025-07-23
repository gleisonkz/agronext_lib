from typing import Optional
from .async_client import BaseAsyncClient
from .quotation_transmission.schemas import (
    TransmissionRequest,
    TransmissionResponse,
)


class PlugSDK:
    def __init__(
        self,
        base_url: str,
        credentials: dict | None = None,
        headers: Optional[dict[str, str]] = None,
    ):
        self.client = BaseAsyncClient(base_url=base_url, headers=headers)
        self.credentials = credentials

    ## Procurement Methods
    async def transmit_quotation(
        self, data: TransmissionRequest
    ) -> TransmissionResponse:
        return await self.client.post(
            endpoint="/propostas/agro",
            payload=data.model_dump(mode="json", by_alias=True),
            response_model=TransmissionResponse,
        )

    async def reject_quotation(self, data: TransmissionRequest) -> TransmissionResponse:
        return await self.client.post(
            endpoint="/propostas/agro/recusar",
            payload=data.model_dump(mode="json", by_alias=True),
        )

    async def issue_policy(self, data: TransmissionRequest) -> TransmissionResponse:
        return await self.client.post(
            endpoint="/apolices/agro",
            payload=data.model_dump(mode="json", by_alias=True),
        )
