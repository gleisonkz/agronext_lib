from typing import Optional

from .async_client import BaseAsyncClient
from .rates import (
    GISAllRatesResponse,
    GISCityRateResponse,
    GISCountryRateResponse,
    GISPixelRateResponse,
    GISRateRequest,
    GISStateRateResponse,
)
from .validations import (
    GISAllValidationsRequest,
    GISAllValidationsResponse,
)

Coordinates = tuple[float, float]
Polygon = list[Coordinates]
Plots = list[Polygon]


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
        polygons: list[Polygon],
        property_location: Coordinates,
    ) -> list[GISAllValidationsResponse]:
        request = GISAllValidationsRequest(polygons)
        return await self.client.post(
            endpoint="/validations/all",
            response_model=list[GISAllValidationsResponse],
            payload=request.model_dump(mode="json", by_alias=True),
        )

    async def get_pixel_rate(
        self,
        polygons: list[list[tuple[float, float]]],
    ) -> list[GISPixelRateResponse]:
        request = GISRateRequest(polygons)
        return await self.client.post(
            endpoint="/rates/pixel",
            response_model=list[GISPixelRateResponse],
            payload=request.model_dump(mode="json", by_alias=True),
        )

    async def get_city_rate(
        self,
        polygons: list[list[tuple[float, float]]],
    ) -> list[GISCityRateResponse]:
        request = GISRateRequest(polygons)
        return await self.client.post(
            endpoint="/rates/city",
            response_model=list[GISCityRateResponse],
            payload=request.model_dump(mode="json", by_alias=True),
        )

    async def get_state_rate(
        self,
        polygons: list[list[tuple[float, float]]],
    ) -> list[GISStateRateResponse]:
        request = GISRateRequest(polygons)
        return await self.client.post(
            endpoint="/rates/state",
            response_model=list[GISStateRateResponse],
            payload=request.model_dump(mode="json", by_alias=True),
        )

    async def get_country_rate(
        self,
        polygons: list[list[tuple[float, float]]],
    ) -> list[GISCountryRateResponse]:
        request = GISRateRequest(polygons)
        return await self.client.post(
            endpoint="/rates/country",
            response_model=list[GISCountryRateResponse],
            payload=request.model_dump(mode="json", by_alias=True),
        )

    async def get_all_rates(
        self,
        polygons: list[list[tuple[float, float]]],
    ) -> list[GISAllRatesResponse]:
        request = GISRateRequest(polygons)
        return await self.client.post(
            endpoint="/rates/all",
            response_model=list[GISAllRatesResponse],
            payload=request.model_dump(mode="json", by_alias=True),
        )
