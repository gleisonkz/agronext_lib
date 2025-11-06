from datetime import date, datetime
from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, Field, RootModel

from ..schemas import Geometry, GeometryArea, GISBaseRequest, Point


class GISAllValidationsRequest(RootModel):
    root: list[GISBaseRequest]


class ProductType(StrEnum):
    fruit_and_vegetables = "fruit_and_vegetables"
    winter_grains = "winter_grains"
    summer_grains = "summer_grains"


class ConflictingPolicyRecord(GeometryArea):
    id: Optional[int] = None
    is_valid: bool
    product_type: ProductType
    contract_end_date: date
    created_at: datetime
    geometry: list[Geometry]


class ConflictingPolicy(BaseModel):
    is_valid: bool
    product_type: Optional[ProductType] = None
    records: list[ConflictingPolicyRecord]


class CityBelongingRecord(GeometryArea):
    is_valid: bool
    uf: Optional[str] = None
    description: Optional[str] = None


class CityBelonging(BaseModel):
    is_valid: bool
    uf: Optional[str] = None
    city: Optional[str] = None
    city_percentage: float
    records: list[CityBelongingRecord]


class DistanceRecord(BaseModel):
    is_valid: bool
    distance_in_meters: float
    from_: Point = Field(alias="from")
    to: Point
    geometry: Geometry


class Distance(BaseModel):
    is_valid: bool
    records: list[DistanceRecord]


class Car(GeometryArea):
    layer: str
    description: Optional[str] = None
    geometry: list[Geometry]


class ProhibitedPolygons(GeometryArea):
    layer: str
    description: Optional[str] = None
    geometry: list[Geometry]


class GISAllValidationsResponse(BaseModel):
    prohibited_polygons: list[ProhibitedPolygons]
    car: list[Car]
    distance: Distance
    city_belonging: CityBelonging
    conflicting_policy: ConflictingPolicy

    pixel_rate: list = Field(..., description="Rate of pixel grid")
    city_rate: list = Field(..., description="Rate of city area")
    state_rate: list = Field(..., description="Rate of state area")
    country_rate: list = Field(..., description="Rate of country area")
