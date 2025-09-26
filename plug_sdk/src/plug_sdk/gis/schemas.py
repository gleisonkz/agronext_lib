from datetime import date, datetime
from enum import Enum
from typing import List, Optional, Tuple

from pydantic import BaseModel, Field, RootModel


class GISAllValidations(BaseModel):
    geometry: List[Tuple[float, float]] = Field(..., description="Polygon to validate")

    uf: Optional[str] = Field(None, description="State to validate")
    city: Optional[str] = Field(None, description="City to validate")
    city_percentage: Optional[float] = Field(None, description="How much city polygon must overlap to validate")

    product_type: Optional[str] = Field(None, description="Product type to compare to another policy to validate")
    max_overlap: Optional[float] = Field(None, description="How much another policy polygon can overlap to validate")


class GISAllValidationsRequest(RootModel):
    root: list[GISAllValidations]


class ProductType(str, Enum):
    fruit_and_vegetables = "fruit_and_vegetables"
    winter_grains = "winter_grains"
    summer_grains = "summer_grains"


class Longitude(RootModel):
    root: float


class Latitude(RootModel):
    root: float


class Point(RootModel):
    root: tuple[Longitude, Latitude]

    model_config = {
        "json_schema_extra": {
            "examples": [
                [0, 0]
            ]
        }
    }


class Geometry(RootModel):
    root: list[Point]


class GeometryArea(BaseModel):
    area_cell_m2: float
    area_input_m2: float
    area_intersection_m2: float
    percentual_input_intersection: float


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

    pixel_rate: List = Field(..., description="Rate of pixel grid")
    city_rate: List = Field(..., description="Rate of city area")
    state_rate: List = Field(..., description="Rate of state area")
    country_rate: List = Field(..., description="Rate of country area")
