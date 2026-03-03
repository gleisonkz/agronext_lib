from typing import List, Optional, Tuple

from pydantic import BaseModel, Field, RootModel


class CroquiPolygon(BaseModel):
    label: str
    coordinates: list[tuple[float, float]]


class CroquiOptions(BaseModel):
    # image size and padding
    width: int = 512
    height: int = 384
    pad_px: int = 40

    # Google Static Maps
    use_google_basemap: bool = True
    maptype: str = "roadmap"  # "roadmap", "satellite", "hybrid", "terrain"
    scale: int = 2  # 1 or 2 (2 gives higher-res)

    # Polygon styling
    outline_width: int = 2
    outline_rgba: Tuple[int, int, int, int] = (0, 80, 200, 255)
    fill_rgba: Tuple[int, int, int, int] = (0, 80, 200, 80)

    # Label styling
    label_fill_rgba: Tuple[int, int, int, int] = (0, 0, 0, 255)
    label_bg_rgba: Tuple[int, int, int, int] = (255, 255, 255, 220)
    label_padding_px: int = 6


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
