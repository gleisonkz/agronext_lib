"""The wire vocabulary every capability shares: the base model, pages, GeoJSON.

The API speaks camelCase and this package speaks snake_case; one alias
generator, declared here, is the whole translation. Models are the SDK's OWN,
ported from the API's schemas: a response model IGNORES fields it does not know,
so an API that grows a field never breaks a caller on an older SDK (§21.3/§23.4).
"""

import enum
from collections.abc import Mapping, Sequence
from datetime import date
from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

#: A GeoJSON geometry, EPSG:4326, as it travels. A mapping and not a typed union:
#: an answer can carry any geometry type, a GeometryCollection included.
type GeoJson = dict[str, Any]

#: (longitude, latitude), EPSG:4326.
type LonLat = tuple[float, float]

#: west, south, east, north — EPSG:4326.
type BoundingBox = tuple[float, float, float, float]


@runtime_checkable
class SupportsGeoInterface(Protocol):
    """Anything exposing `__geo_interface__` — a shapely geometry, for instance."""

    @property
    def __geo_interface__(self) -> Mapping[str, Any]: ...


#: What a method taking a geometry accepts.
type GeometryInput = Mapping[str, Any] | SupportsGeoInterface


def to_geojson(geometry: GeometryInput) -> GeoJson:
    """A geometry as the API takes it: a plain GeoJSON mapping."""
    if isinstance(geometry, SupportsGeoInterface):
        return dict(geometry.__geo_interface__)
    return dict(geometry)


class WireModel(BaseModel):
    """Every request and response model of this package.

    Frozen: an answer is a record of what the API said. `extra="ignore"`: a field
    the API added after this version is dropped, never an error.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="ignore",
        frozen=True,
    )


class Page[ItemT: WireModel](WireModel):
    """A page of a listing: 1-based `page`, the `size` served, and the totals."""

    items: Sequence[ItemT]
    page: int
    size: int
    total: int
    pages: int


class SnapshotReference(WireModel):
    """C-5's provenance block: which dated copy of a source an answer read.

    `caveat` is a limitation of the SOURCE; `stale` is about the API's copy.
    """

    source_key: str
    label: str
    authority: str
    kind: str
    snapshot_id: int
    fetched_at: date
    age_days: int
    stale: bool
    dataset_version: str | None = None
    url: str | None = None
    caveat: str | None = None
    #: None for a national source; otherwise the UFs it covers.
    covers_states: Sequence[str] | None = None


class LayerReference(WireModel):
    """Which área an answer came from, and at which level."""

    area_id: int
    level: str
    name: str | None = None
    country_id: int | None = None
    state_id: int | None = None
    municipality_id: int | None = None


# --------------------------------------------------------------------------- #
# Vocabularies the API exposes on the wire
# --------------------------------------------------------------------------- #


class LayerLevel(enum.StrEnum):
    """Where an área sits in the hierarchy — and therefore its precedence."""

    COUNTRY = "country"
    STATE = "state"
    MUNICIPALITY = "municipality"
    CAR = "car"
    CUSTOM = "custom"


class RateMode(enum.StrEnum):
    """How a (safra, produto) prices its franquias."""

    DEDUCTIBLE = "deductible"
    RATIO = "ratio"


class RateWriteOperation(enum.StrEnum):
    """What one row of a rate or adjustment trail did."""

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class ScopeList(enum.StrEnum):
    """The abrangência's two outlines."""

    ALLOWED = "allowed"
    FORBIDDEN = "forbidden"


class LayerRevisionOperation(enum.StrEnum):
    """What one revision of an área recorded."""

    CREATE = "create"
    UPDATE_GEOMETRY = "update_geometry"
    UPDATE_NAME = "update_name"
    RETIRE = "retire"
    BOUNDARY_REFRESH = "boundary_refresh"


class RunKind(enum.StrEnum):
    """What a pinned run answered."""

    SCREENING = "screening"
    RATE_RESOLUTION = "rate_resolution"


class RegistryKind(enum.StrEnum):
    """What kind of registry a screening source is."""

    REGISTRY = "registry"
    ENFORCEMENT = "enforcement"
    RESTRICTION = "restriction"
    SUPPLEMENTARY = "supplementary"
    BOUNDARY = "boundary"


class BrazilianState(enum.StrEnum):
    """The 27 UFs, by abbreviation."""

    AC = "AC"
    AL = "AL"
    AP = "AP"
    AM = "AM"
    BA = "BA"
    CE = "CE"
    DF = "DF"
    ES = "ES"
    GO = "GO"
    MA = "MA"
    MT = "MT"
    MS = "MS"
    MG = "MG"
    PA = "PA"
    PB = "PB"
    PR = "PR"
    PE = "PE"
    PI = "PI"
    RJ = "RJ"
    RN = "RN"
    RS = "RS"
    RO = "RO"
    RR = "RR"
    SC = "SC"
    SP = "SP"
    SE = "SE"
    TO = "TO"


__all__ = [
    "BoundingBox",
    "BrazilianState",
    "GeoJson",
    "GeometryInput",
    "LayerLevel",
    "LayerReference",
    "LayerRevisionOperation",
    "LonLat",
    "Page",
    "RateMode",
    "RateWriteOperation",
    "RegistryKind",
    "RunKind",
    "ScopeList",
    "SnapshotReference",
    "SupportsGeoInterface",
    "WireModel",
    "to_geojson",
]
