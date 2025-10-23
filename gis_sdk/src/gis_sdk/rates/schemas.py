from pydantic import BaseModel, RootModel

from gis_sdk.schemas import GISBaseRequest, GeometryArea, Geometry


class GISRateRequest(RootModel):
    root: list[GISBaseRequest]


class Product(BaseModel):
    id: int
    name: str


class Franchise(BaseModel):
    id: int
    name: str


class Profile(BaseModel):
    id: int
    name: str


class Rate(BaseModel):
    commercial: float
    technical: float


class PixelRate(GeometryArea):
    geometry: list[Geometry]
    product: Product
    franchise: Franchise
    profile: Profile
    rate: Rate


class GISPixelRateResponse(BaseModel):
    input_geometry: list[list[float, float]]
    pixel_rate: list[PixelRate]


class CityRate(GeometryArea):
    geometry: list[Geometry]
    rate: float
    uf: str
    description: str


class GISCityRateResponse(BaseModel):
    input_geometry: list[list[float, float]]
    city_rate: list[CityRate]


class StateRate(GeometryArea):
    geometry: list[Geometry]
    rate: float
    uf: str
    description: str


class GISStateRateResponse(BaseModel):
    input_geometry: list[list[float, float]]
    state_rate: list[StateRate]


class CountryRate(GeometryArea):
    geometry: list[Geometry]
    rate: float
    country: str
    description: str


class GISCountryRateResponse(BaseModel):
    input_geometry: list[list[float, float]]
    country_rate: list[CountryRate]


class GISAllRatesResponse(BaseModel):
    input_geometry: list[list[float, float]]
    pixel_rate: list[PixelRate]
    city_rate: list[CityRate]
    state_rate: list[StateRate]
    country_rate: list[CountryRate]
