"""The rates capability's wire models: produtos, franquias, safras, each
(safra, produto)'s configuration, the rates themselves and their resolution.

Ported from the API's rates schemas. Rates, fatores, franquias, percents and
yields are exact `Decimal`s on both sides of the wire. A PRODUTIVIDADE ESPERADA
is always kg/ha — the `_kg_ha` in its name is the unit, and converting to t/ha
is the caller's to do.
"""

import datetime
import decimal
from collections.abc import Sequence

from agronext_gis_sdk._wire import (
    BoundingBox,
    GeoJson,
    LayerLevel,
    LayerReference,
    RateMode,
    RateWriteOperation,
    ScopeList,
    WireModel,
)

# --------------------------------------------------------------------------- #
# Produtos and franquias
# --------------------------------------------------------------------------- #


class ProductItem(WireModel):
    """A produto. Its identity is the unique code."""

    id: int
    code: str
    name: str | None = None
    crop: str | None = None
    peril: str | None = None
    #: Every rate written for this produto must carry `expected_yield_kg_ha`.
    yield_required: bool
    retired_at: datetime.datetime | None = None


class ProductResponse(ProductItem):
    pass


class ProductCreateRequest(WireModel):
    code: str
    name: str | None = None
    crop: str | None = None
    peril: str | None = None
    yield_required: bool = False


class ProductUpdateRequest(WireModel):
    """The whole form: a field sent as None CLEARS it, and `yield_required`
    left out is False — send the produto's current value to keep it."""

    name: str | None = None
    crop: str | None = None
    peril: str | None = None
    yield_required: bool = False


class DeductibleItem(WireModel):
    """A franquia: one value of a produto's predetermined set."""

    id: int
    product_id: int
    value: decimal.Decimal
    retired_at: datetime.datetime | None = None


class DeductibleResponse(DeductibleItem):
    pass


class DeductibleCreateRequest(WireModel):
    value: decimal.Decimal


# --------------------------------------------------------------------------- #
# Safras, and copying a produto from one into another
# --------------------------------------------------------------------------- #


class SeasonItem(WireModel):
    """A safra: a free label, and the period it runs for (both dates or neither)."""

    id: int
    label: str
    ordinal: int
    #: The live safra whose period starts last.
    is_latest: bool
    starts_on: datetime.date | None = None
    ends_on: datetime.date | None = None
    #: Today falls inside the period.
    is_open: bool = False
    retired_at: datetime.datetime | None = None
    product_count: int = 0


class SeasonResponse(SeasonItem):
    product_ids: Sequence[int] = ()


class PlantingWindowDeclaration(WireModel):
    """One planting window of a declared set. Dates inclusive at both ends."""

    label: str
    starts_on: datetime.date
    ends_on: datetime.date


class ProductCopyDeclaration(WireModel):
    """One produto made IDENTICAL to itself in `from_season_id` — abrangência as
    saved, fatores, rates, bonificações/agravamentos, disputas — replacing what
    it held in the target safra.

    `windows` are its planting windows in the TARGET safra, never copied: None
    (not declared) is refused when the source has windows; `[]` is "no windows".
    """

    product_id: int
    from_season_id: int
    windows: Sequence[PlantingWindowDeclaration] | None = None


class SeasonCreateRequest(WireModel):
    label: str
    #: None: after every existing safra. The order of safras is their period.
    ordinal: int | None = None
    starts_on: datetime.date | None = None
    ends_on: datetime.date | None = None
    product_ids: Sequence[int] = ()
    #: Duplicar: produtos copied from other safras, in the same transaction.
    copies: Sequence[ProductCopyDeclaration] = ()


class SeasonUpdateRequest(WireModel):
    label: str
    starts_on: datetime.date | None = None
    ends_on: datetime.date | None = None


class SeasonProductsRequest(WireModel):
    """The WHOLE set of produtos a safra sells, and any copied into it in the same save."""

    product_ids: Sequence[int]
    copies: Sequence[ProductCopyDeclaration] = ()


class CopyCountItem(WireModel):
    """What one piece of a copy did in the target."""

    written: int
    removed: int
    unchanged: int


class PairCopyResponse(WireModel):
    """One produto copied."""

    season_id: int
    product_id: int
    from_season_id: int
    from_season_label: str
    rate_mode: RateMode
    ratios: CopyCountItem
    pieces: CopyCountItem
    rates: CopyCountItem
    adjustments: CopyCountItem
    contest_count: int
    window_count: int


class SeasonWithCopiesResponse(SeasonResponse):
    """The safra as saved, and what the same act copied into it."""

    copies: Sequence[PairCopyResponse] = ()


# --------------------------------------------------------------------------- #
# One (safra, produto): planting windows, pricing mode, abrangência, contests
# --------------------------------------------------------------------------- #


class PlantingWindowItem(WireModel):
    """A period a safra covers planting a produto in."""

    id: int
    season_id: int
    product_id: int
    label: str
    starts_on: datetime.date
    ends_on: datetime.date
    retired_at: datetime.datetime | None = None


class PlantingWindowsRequest(WireModel):
    """The WHOLE set of windows: none, or two or more."""

    windows: Sequence[PlantingWindowDeclaration] = ()


class PairConfigurationResponse(WireModel):
    """What one (safra, produto) holds, counted, and its planting windows."""

    season_id: int
    product_id: int
    rate_mode: RateMode
    ratio_count: int
    scope_saved: bool
    allowed_piece_count: int
    forbidden_piece_count: int
    rate_count: int
    adjustment_count: int
    contest_count: int
    windows: Sequence[PlantingWindowItem] = ()


class DeductibleRatioItem(WireModel):
    """A franquia and its fatores over the reference layer (None: no layer)."""

    deductible_id: int
    value: decimal.Decimal
    retired_at: datetime.datetime | None = None
    commercial_ratio: decimal.Decimal | None = None
    risk_ratio: decimal.Decimal | None = None


class PricingResponse(WireModel):
    """`deductible`: each franquia has its own layer. `ratio`: one reference layer,
    times each franquia's fatores."""

    season_id: int
    product_id: int
    mode: RateMode
    ratios: Sequence[DeductibleRatioItem] = ()


class DeductibleRatioRequest(WireModel):
    """Both fatores, or neither for "no layer"."""

    deductible_id: int
    commercial_ratio: decimal.Decimal | None = None
    risk_ratio: decimal.Decimal | None = None


class PricingRequest(WireModel):
    """The mode and the WHOLE fator table."""

    mode: RateMode
    ratios: Sequence[DeductibleRatioRequest] = ()


class ScopePieceItem(WireModel):
    """One catálogo área an abrangência outline was built from."""

    area_id: int
    outline: ScopeList
    level: LayerLevel
    name: str | None = None
    state_abbr: str | None = None
    area_ha: float
    retired_at: datetime.datetime | None = None
    #: Its shape changed since the outline was saved; saving again takes it.
    changed_since_save: bool = False


class ScopeResponse(WireModel):
    """The abrangência as saved: the liberada (`allowed`) and the proibida.

    The outlines are simplified for transport (EPSG:4326); `saved_at` is None
    when it was never saved — sold nowhere yet.
    """

    season_id: int
    product_id: int
    allowed: GeoJson | None = None
    forbidden: GeoJson | None = None
    allowed_ha: float = 0.0
    forbidden_ha: float = 0.0
    saved_at: datetime.datetime | None = None
    saved_by_username: str | None = None
    pieces: Sequence[ScopePieceItem] = ()


class ScopeRequest(WireModel):
    """The áreas each outline is built from, WHOLE."""

    allowed_area_ids: Sequence[int] = ()
    forbidden_area_ids: Sequence[int] = ()


class RemovedRateItem(WireModel):
    """A rate a save would remove: its área no longer reaches the liberada."""

    area_id: int
    level: LayerLevel
    name: str | None = None
    deductible_id: int | None = None
    deductible_value: decimal.Decimal | None = None
    value: decimal.Decimal
    risk_value: decimal.Decimal


class RemovedAdjustmentItem(WireModel):
    area_id: int
    name: str | None = None
    percent: decimal.Decimal


class ScopePreviewResponse(WireModel):
    """What saving would do, without doing it."""

    scope: ScopeResponse
    changed_pieces: Sequence[ScopePieceItem] = ()
    removed_rates: Sequence[RemovedRateItem] = ()
    removed_adjustments: Sequence[RemovedAdjustmentItem] = ()


class ScopeAreaItem(WireModel):
    """A catálogo área that overlaps the liberada — one a rate may be written on."""

    area_id: int
    level: LayerLevel
    name: str | None = None
    state_id: int | None = None
    state_abbr: str | None = None
    area_ha: float
    retired_at: datetime.datetime | None = None
    #: It reaches into the proibida: its rate does not resolve there.
    forbidden: bool = False
    contest_count: int = 0


class ScopeLevelCount(WireModel):
    level: LayerLevel
    count: int


class ScopeSummaryResponse(WireModel):
    """How many catálogo áreas the liberada reaches, per level, and its UFs.
    `car_count` only when one UF was asked for."""

    levels: Sequence[ScopeLevelCount] = ()
    car_count: int | None = None
    state_ids: Sequence[int] = ()


class ScopeOutlineResponse(WireModel):
    """The áreas an Em massa act reaches, and their union for a map (simplified
    to 100 m). `geometry` is None when it reaches none."""

    area_count: int
    geometry: GeoJson | None = None


class SoldMunicipalityItem(WireModel):
    municipality_id: int
    name: str
    state_id: int
    deductible_ids: Sequence[int] = ()


class SoldTerritoryItem(WireModel):
    """A UF, and its municípios where a rate has been written inside the liberada."""

    state_id: int
    abbr: str
    name: str
    municipalities: Sequence[SoldMunicipalityItem] = ()


class ContestMemberItem(WireModel):
    """One polygon's place in one contest. Position 1 wins."""

    area_id: int
    name: str | None = None
    position: int


class ContestItem(WireModel):
    """Custom polygons that all cover the same ground, in winning order."""

    id: int
    members: Sequence[ContestMemberItem]


class ContestOrderRequest(WireModel):
    """The contest's members in their new order — the same members. First wins."""

    area_ids: Sequence[int]


# --------------------------------------------------------------------------- #
# Bonificação & agravamento
# --------------------------------------------------------------------------- #


class CarAdjustmentItem(WireModel):
    """A CAR imóvel's percent on the commercial rate: negative a bonus, positive a malus."""

    area_id: int
    name: str | None = None
    state_abbr: str | None = None
    percent: decimal.Decimal
    retired_at: datetime.datetime | None = None
    updated_at: datetime.datetime
    updated_by_username: str


class CarAdjustmentOperationRequest(WireModel):
    """One imóvel: a percent to set, or None to clear it."""

    area_id: int
    percent: decimal.Decimal | None


class CarAdjustmentBatchRequest(WireModel):
    note: str | None = None
    operations: Sequence[CarAdjustmentOperationRequest]


class CarAdjustmentResultItem(WireModel):
    area_id: int
    operation: RateWriteOperation
    percent: decimal.Decimal | None = None
    previous_percent: decimal.Decimal | None = None


class CarAdjustmentBatchResponse(WireModel):
    batch_id: int
    written_at: datetime.datetime
    operation_count: int
    results: Sequence[CarAdjustmentResultItem]


class CarAdjustmentWriteItem(WireModel):
    """One row of the adjustments' trail."""

    id: int
    batch_id: int
    area_id: int
    name: str | None = None
    operation: RateWriteOperation
    percent: decimal.Decimal | None = None
    previous_percent: decimal.Decimal | None = None
    note: str | None = None
    written_at: datetime.datetime
    written_by_username: str


# --------------------------------------------------------------------------- #
# The rates, written
# --------------------------------------------------------------------------- #


class RateItem(WireModel):
    """One written rate and the área it is written on. `deductible_id` None: the
    reference layer."""

    id: int
    season_id: int
    product_id: int
    deductible_id: int | None = None
    layer: LayerReference
    value: decimal.Decimal
    risk_value: decimal.Decimal
    #: The cell's produtividade esperada, kg/ha. None: none stated.
    expected_yield_kg_ha: decimal.Decimal | None = None
    order: int | None = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    updated_by_username: str


class RateCellSummaryItem(WireModel):
    """What one célula holds at one level."""

    season_id: int
    product_id: int
    deductible_id: int | None = None
    level: LayerLevel
    layer_count: int
    min_value: decimal.Decimal | None = None
    max_value: decimal.Decimal | None = None
    min_risk_value: decimal.Decimal | None = None
    max_risk_value: decimal.Decimal | None = None
    last_written_at: datetime.datetime | None = None


class RateWriteOperationRequest(WireModel):
    """One cell of one act: both rates to write, or neither to delete.

    `deductible_id` None writes the reference layer. A write states the WHOLE
    cell: `expected_yield_kg_ha` left out means the cell holds none afterwards,
    and a produto with `yield_required` refuses that
    (`rates.write.yield_required`). A delete carries no yield.
    """

    season_id: int
    product_id: int
    deductible_id: int | None
    area_id: int
    value: decimal.Decimal | None = None
    risk_value: decimal.Decimal | None = None
    expected_yield_kg_ha: decimal.Decimal | None = None


class RateWriteBatchRequest(WireModel):
    """One act: every operation lands, or none does."""

    note: str | None = None
    operations: Sequence[RateWriteOperationRequest]


class RateWriteResultItem(WireModel):
    area_id: int
    operation: RateWriteOperation
    value: decimal.Decimal | None = None
    previous_value: decimal.Decimal | None = None
    risk_value: decimal.Decimal | None = None
    previous_risk_value: decimal.Decimal | None = None
    expected_yield_kg_ha: decimal.Decimal | None = None
    previous_expected_yield_kg_ha: decimal.Decimal | None = None
    area_level: str


class RateWriteBatchResponse(WireModel):
    batch_id: int
    written_at: datetime.datetime
    operation_count: int
    results: Sequence[RateWriteResultItem]


class RateWriteItem(WireModel):
    """One row of the rate trail."""

    id: int
    batch_id: int
    season_id: int
    product_id: int
    deductible_id: int | None = None
    area_id: int
    area_name: str | None = None
    operation: RateWriteOperation
    value: decimal.Decimal | None = None
    previous_value: decimal.Decimal | None = None
    risk_value: decimal.Decimal | None = None
    previous_risk_value: decimal.Decimal | None = None
    expected_yield_kg_ha: decimal.Decimal | None = None
    previous_expected_yield_kg_ha: decimal.Decimal | None = None
    area_level: str
    written_at: datetime.datetime
    written_by_username: str


class RateWriteBatchItem(WireModel):
    """The trail at the act grain: what one person changed on one occasion."""

    id: int
    written_at: datetime.datetime
    written_by_username: str
    note: str | None = None
    operation_count: int


# --------------------------------------------------------------------------- #
# Resolution: the rate over a polygon
# --------------------------------------------------------------------------- #


class RateResolutionPreflightRequest(WireModel):
    geometry: GeoJson
    cell_m: int | None = None


class GridOptionItem(WireModel):
    """One grid resolution, and whether this extent can be served at it."""

    cell_m: int
    tile_count: int
    within_budget: bool


class RateResolutionPreflightResponse(WireModel):
    area_ha: float
    tile_budget: int
    options: Sequence[GridOptionItem]
    recommended_cell_m: int


class RateResolutionRequest(WireModel):
    """A resolution: `season_id` None asks the latest safra; `cell_m` is one of 10, 30,
    100 or 250."""

    geometry: GeoJson
    season_id: int | None = None
    product_id: int
    deductible_id: int
    cell_m: int


class LayerAdjustmentItem(WireModel):
    """The bonificação/agravamento on a layer's tiles, and the rate before it."""

    area_id: int
    name: str | None = None
    percent: decimal.Decimal
    unadjusted_value: decimal.Decimal


class ResolvedLayerItem(WireModel):
    """An área that won tiles, the rate it gave them, and its share of the answer."""

    index: int
    area_id: int
    level: LayerLevel
    name: str | None = None
    rank: int
    value: decimal.Decimal
    risk_value: decimal.Decimal
    #: kg/ha, never under a fator or a bonificação/agravamento. None: none stated.
    expected_yield_kg_ha: decimal.Decimal | None = None
    order: int | None = None
    tile_count: int
    #: The ground this entry priced, in hectares: its weight. The aggregate is
    #: sum(value * area_ha) / sum(area_ha), rounded half-up to the rate's quantum.
    area_ha: float
    share_pct: float
    adjustment: LayerAdjustmentItem | None = None
    #: In `ratio` mode, the reference layer's rates before the fator:
    #: reference_value * commercial_ratio is `adjustment.unadjusted_value` (or
    #: `value`, unadjusted), and that * (1 + percent/100) is `value`, each step
    #: rounded half-even to the rate's quantum. None in `deductible` mode.
    reference_value: decimal.Decimal | None = None
    reference_risk_value: decimal.Decimal | None = None


class RateGrid(WireModel):
    """The answer per tile, anchored in EPSG:5880: `origin_x`/`origin_y` are the
    north-west corner, columns run east and rows south, and `cells` is row-major.
    Each cell is an index into the answer's `layers`, or -1 where nothing
    resolved — which a cell outside the query polygon also carries."""

    srid: int
    cell_m: int
    origin_x: float
    origin_y: float
    cols: int
    rows: int
    bbox_4326: BoundingBox
    cells: Sequence[int]


class RateResolutionResponse(WireModel):
    """The rate per tile and the area-weighted aggregate. `run_id` pins it."""

    run_id: int
    season_id: int
    product_id: int
    deductible_id: int
    mode: RateMode = RateMode.DEDUCTIBLE
    commercial_ratio: decimal.Decimal | None = None
    risk_ratio: decimal.Decimal | None = None
    cell_m: int
    aggregate_value: decimal.Decimal | None = None
    aggregate_risk_value: decimal.Decimal | None = None
    #: kg/ha over the same tiles as the rates; None unless every tile states one.
    aggregate_expected_yield_kg_ha: decimal.Decimal | None = None
    #: The polygon as its tiles measure it, in hectares: the aggregates'
    #: denominator, and the sum of the layers' `area_ha`.
    area_ha: float
    tile_count: int
    resolved_tile_count: int
    unresolved_tile_count: int
    unresolved_area_pct: float
    tile_budget: int
    layers: Sequence[ResolvedLayerItem]
    grid: RateGrid


class RateHeatmapRequest(WireModel):
    """One franquia's rate surface over the liberada inside `bbox`
    (west, south, east, north — EPSG:4326)."""

    season_id: int | None = None
    product_id: int
    deductible_id: int
    cell_m: int
    bbox: BoundingBox


class RateHeatmapResponse(WireModel):
    """A surface, not a resolution: nothing refused, nothing pinned. `grid` None when
    the box misses the liberada."""

    cell_m: int
    effective_cell_m: int
    mode: RateMode = RateMode.DEDUCTIBLE
    commercial_ratio: decimal.Decimal | None = None
    risk_ratio: decimal.Decimal | None = None
    layers: Sequence[ResolvedLayerItem] = ()
    grid: RateGrid | None = None
    unresolved_cells: Sequence[int] = ()
    forbidden_cells: Sequence[int] = ()


class RateResolutionRunItem(WireModel):
    """A pinned resolution, so a resolved number stays defensible."""

    id: int
    requested_at: datetime.datetime
    as_of: datetime.datetime
    cell_m: int | None = None
    season_id: int | None = None
    product_id: int | None = None
    deductible_id: int | None = None
    tile_count: int | None = None
    unresolved_tile_count: int | None = None
    aggregate_value: decimal.Decimal | None = None
    aggregate_risk_value: decimal.Decimal | None = None
    aggregate_expected_yield_kg_ha: decimal.Decimal | None = None
    requested_by_username: str


class RateResolutionRunResponse(RateResolutionRunItem):
    query_polygon: GeoJson


__all__ = [
    "CarAdjustmentBatchRequest",
    "CarAdjustmentBatchResponse",
    "CarAdjustmentItem",
    "CarAdjustmentOperationRequest",
    "CarAdjustmentResultItem",
    "CarAdjustmentWriteItem",
    "ContestItem",
    "ContestMemberItem",
    "ContestOrderRequest",
    "CopyCountItem",
    "DeductibleCreateRequest",
    "DeductibleItem",
    "DeductibleRatioItem",
    "DeductibleRatioRequest",
    "DeductibleResponse",
    "GridOptionItem",
    "LayerAdjustmentItem",
    "PairConfigurationResponse",
    "PairCopyResponse",
    "PlantingWindowDeclaration",
    "PlantingWindowItem",
    "PlantingWindowsRequest",
    "PricingRequest",
    "PricingResponse",
    "ProductCopyDeclaration",
    "ProductCreateRequest",
    "ProductItem",
    "ProductResponse",
    "ProductUpdateRequest",
    "RateCellSummaryItem",
    "RateGrid",
    "RateHeatmapRequest",
    "RateHeatmapResponse",
    "RateItem",
    "RateResolutionPreflightRequest",
    "RateResolutionPreflightResponse",
    "RateResolutionRequest",
    "RateResolutionResponse",
    "RateResolutionRunItem",
    "RateResolutionRunResponse",
    "RateWriteBatchItem",
    "RateWriteBatchRequest",
    "RateWriteBatchResponse",
    "RateWriteItem",
    "RateWriteOperationRequest",
    "RateWriteResultItem",
    "RemovedAdjustmentItem",
    "RemovedRateItem",
    "ResolvedLayerItem",
    "ScopeAreaItem",
    "ScopeLevelCount",
    "ScopePieceItem",
    "ScopePreviewResponse",
    "ScopeRequest",
    "ScopeResponse",
    "ScopeSummaryResponse",
    "SeasonCreateRequest",
    "SeasonItem",
    "SeasonProductsRequest",
    "SeasonResponse",
    "SeasonUpdateRequest",
    "SeasonWithCopiesResponse",
    "SoldMunicipalityItem",
    "SoldTerritoryItem",
]
