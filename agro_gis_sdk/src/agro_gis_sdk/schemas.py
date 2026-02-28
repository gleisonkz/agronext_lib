from typing import List, Optional, Tuple

from pydantic import BaseModel, Field, RootModel


class CroquiPolygon(BaseModel):
    label: str
    coordinates: list[tuple[float, float]]


class GISBaseRequest(BaseModel):
    geometry: List[Tuple[float, float]] = Field(..., description="Polygon to validate")

    uf: Optional[str] = Field(None, description="State to validate")
    city: Optional[str] = Field(None, description="City to validate")
    city_percentage: Optional[float] = Field(None, description="How much city polygon must overlap to validate")

    product_type: Optional[str] = Field(None, description="Product type to compare to another policy to validate")
    max_overlap: Optional[float] = Field(None, description="How much another policy polygon can overlap to validate")


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
