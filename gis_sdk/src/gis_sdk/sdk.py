from typing import Optional
from .async_client import BaseAsyncClient

from .validations import (
    GISAllValidationsRequest,
    GISAllValidationsResponse,
)


class GisSDK:
    def __init__(
        self,
        base_url: str = "http://absdevagrofebe:8004",
        credentials: dict | None = None,
        headers: Optional[dict[str, str]] = None,
    ):
        self.client = BaseAsyncClient(base_url=base_url, headers=headers)
        self.credentials = credentials

    async def get_gis_report(
        self,
        polygons: list[list[tuple[float, float]]],
    ) -> list[GISAllValidationsResponse]:
        request = GISAllValidationsRequest(polygons)
        return await self.client.post(
            endpoint="/validations/all",
            response_model=list[GISAllValidationsResponse],
            payload=request.model_dump(mode="json", by_alias=True),
        )
