# Changelog

## 0.8.0 — 2026-10-13

`gis.underwriting` is complete: the nine calls of a sale, each ONE request.

- `underwriting.list_open_seasons()` is where a sale starts: the safras being
  sold today, each with the `id` every later call takes. It takes nothing, so
  no id of the flow has to be known in advance. It is `seasons.list_open_seasons`
  at route level, which is unchanged.
- The rate of a sale, over every polygon of it:
  - `underwriting.resolve_rates(polygons, season_id=, product_id=,
    deductible_id=)` returns `RateResolutionPolygonsResponse`: the sale's
    commercial and risk rates, weighted by area over every polygon, and each
    polygon's own rates, layers and `run_id` (`RateResolutionPolygonItem`).
    No grid is named: each polygon is resolved on the finest grid its size
    allows, and its `cell_m` says which.
  - It is all or nothing. A polygon that cannot be resolved raises
    `PolygonsRefusedError` (an `UnprocessableError`,
    `rates.resolve.polygons_refused`), whose `refusals` name every polygon that
    failed: `PolygonRefusal` with `polygon_index`, `code`, `detail` and
    `context`. `RateRefusalCode` lists the reasons.
  - At route level: `rates.resolve_polygons(geometries, product_id=,
    deductible_id=, season_id=None, cell_m=None)`.
- `rates.resolve` no longer needs a grid: `cell_m` is optional, and None
  resolves on the finest grid the tile budget affords. The answer's `cell_m` is
  the grid used. Passing one behaves as before.
- While the polygons are drawn:
  - `underwriting.list_car_properties(polygon)` is the CAR imóveis one polygon
    touches, to pick the one it belongs to.
  - `underwriting.validate_group(polygons, municipality_id=,
    min_shared_municipality_pct=None)` is whether they may go in one contract,
    in the município the sale is in.
- After the purchase, the contract's three screenings:
  - `underwriting.screen_car_properties(car_codes)` takes CAR codes and nothing
    else.
  - `underwriting.screen_polygons(polygons)` returns `OverlapsPolygonsResponse`:
    the registry features over each polygon (`OverlapsPolygonItem`), with the
    sources once. At route level: `screening.overlaps_polygons(geometries,
    limit=None)`.
  - `underwriting.check_policy_overlap(polygons, product_id=None,
    season_ids=None, running_only=True, planting_window_ids=None)` returns
    `PolicyOverlapPolygonsResponse`: each polygon's collisions
    (`PolicyOverlapPolygonItem`) and the total. At route level:
    `policies.check_polygons_overlap(PolicyOverlapPolygonsRequest(...))`.
- A request about several polygons that names one the API cannot read is
  refused with `geometry.invalid`, and its `context["polygon_index"]` says
  which. No polygon, or more than the deployment allows (12 by default), is
  refused with `rates.resolve.polygon_count`,
  `screening.overlaps.polygon_count` or `policies.overlap.polygon_count`.
- `example.py` is rewritten around these calls, and is how the SDK is validated
  against a live API: the client as a dependency, one function per call, and a
  command that walks a whole sale over the network. `--season-id`,
  `--municipality-id`, `--product-id` and `--deductible-id` name what a buyer
  would pick; unnamed, the safra is the one open today and the rest the first
  offered. It prints the id of everything an option can name before picking
  from it. It ends `9 calls answered`, or non-zero: 2 when it could not go on,
  1 when a request failed. It needs `typer` and
  `pydantic-settings`, both development dependencies — the wheel is unchanged.
- Nothing was removed or renamed. Every route-level method is unchanged, apart
  from `rates.resolve`'s `cell_m` becoming optional.

## 0.7.0 — 2026-10-13

- `gis.underwriting`: the calls a sale makes, in the order it makes them. Each
  takes what the caller holds at that step and returns what the next one needs.
  The first two:
  - `list_sold_territory(season_id)` is where anything is on sale in a safra:
    only the states that have produtos and, under each, only the municípios
    with rates. It returns `SeasonTerritoryResponse`.
  - `list_products_on_sale(season_id, municipality_id)` is what is sold in one
    município, by its IBGE code: each produto with its `crop`, its `peril` and
    the franquias on offer there, as `id` and `value`. It returns
    `ProductsOnSaleResponse`. An unknown code or safra raises `NotFoundError`.
- The same two calls at route level, `seasons.list_sold_territory` and
  `seasons.list_products_on_sale`, and `rates.refresh_sold_territory()`, which
  asks the API to refresh that listing now and waits for it.
- Both answers carry `refreshed_at`. The API holds this listing and refreshes
  it after the writes that change what is on sale; the instant says how old
  the answer is. A rate is never read from it.
- New models: `SeasonTerritoryResponse`, `SoldStateItem`, `SoldPlaceItem`,
  `ProductsOnSaleResponse`, `OnSaleProductItem`, `SoldTerritoryRefreshResponse`.
- Nothing was removed or renamed. `pairs.territory(season_id, product_id)`, the
  listing for one produto, is unchanged.

## 0.6.0 — 2026-09-30

- A resolution carries every parameter of its own arithmetic, so a caller can
  check it from the answer alone:
  - `RateResolutionResponse.area_ha` is the polygon as its tiles measure it,
    and the aggregates' denominator.
  - `ResolvedLayerItem.area_ha` is the ground each entry priced, and its weight:
    `aggregate_value = sum(value * area_ha) / sum(area_ha)`, rounded half-up to
    the rate's quantum. The same applies to the risk rate and the yield.
  - `ResolvedLayerItem.reference_value` and `reference_risk_value` are, in
    `ratio` mode, the reference layer's rates before the fator. They are
    `value`'s inputs, with `commercial_ratio`/`risk_ratio` and the
    bonificação/agravamento's `adjustment.percent`. They are None in
    `deductible` mode.
  - The heatmap's layers carry `area_ha` and the reference rates too.
- `groups.validate` answers one polygon too, and takes two parameters:
  - `municipality_id` is the IBGE code of the município the proposal
    declares. The group is anchored in that município rather than in the one
    the polygons share: each polygon needs a vertex in it, and its minimum
    share inside it. An unknown code is refused with
    `groups.validate.unknown_municipality`.
  - `min_shared_municipality_pct` is this request's minimum share. Without
    it, the deployment's setting applies, and `thresholds` reports the one
    used.
  - Zero polygons are still refused (`groups.validate.polygon_count`), and so
    are more than the ceiling.
- `PolicyOverlapRequest` with no `season_ids` asks the safras open today. The
  API's own description said every safra; the behaviour never changed.

## 0.5.0 — 2026-09-28

- Pastas for regions: `regions.list_folders`, `create_folder`, `rename_folder`
  and `delete_folder` (refused `areas.region_folder.not_empty` while a live
  region is filed in it), with `RegionFolderItem`, `RegionFolderList` and
  `RegionFolderRequest`. A pasta only organizes; nothing else reads it.
- `RegionItem.folder_id`/`folder_name`; `list_regions(folder_id=…, unfiled=…)`;
  the listing is ordered by pasta, then name.
- `RegionCreateRequest.folder_id` and `RegionUpdateRequest.folder_id`. The
  update is the whole form: leaving `folder_id` out files the region in "Sem
  pasta", so send its current pasta to keep it.
- A region name is unique within its pasta among the live regions, no longer
  across every region (`areas.region.name_taken`).
- `pairs.scope_outline(season_id, product_id, region_id=…, state_id=…,
  level=…)` returns `ScopeOutlineResponse`: the áreas an Em massa act reaches,
  narrowed as `list_scope_areas` narrows them. It gives their count and their
  union as one outline, simplified to 100 m. It needs `region_id` or
  `state_id`.

## 0.4.0 — 2026-09-27

- **Breaking:** `screening.preflight` takes an AREA (Polygon or MultiPolygon).
  The API refuses a point now (`geometry.invalid`): a point listed the imóveis
  under it with no overlap and could go no further, and nothing used it.
- `ScreeningCandidate.overlap_ha` and `overlap_pct` are always present — they
  were only ever missing for a point.

## 0.3.0 — 2026-09-27

- The produtividade esperada, in kg/ha on every field that carries it (the
  `_kg_ha` suffix is the unit; t/ha is the caller's to convert):
  `RateWriteOperationRequest.expected_yield_kg_ha`, `RateItem`,
  `RateWriteResultItem` and `RateWriteItem` (with the value it replaced),
  `ResolvedLayerItem`, and `aggregate_expected_yield_kg_ha` on
  `RateResolutionResponse` and the pinned runs.
- `ProductItem.yield_required`, set through `ProductCreateRequest` and
  `ProductUpdateRequest`: when on, a rate written without a yield is refused
  `rates.write.yield_required`. The update is the whole form, so send the
  current value to keep it.
- `RateResolutionRunResponse.aggregate_risk_value` is now filled: the API
  pinned it and did not return it.

## 0.2.0 — 2026-09-26

- `areas.list_areas`, `areas.list_area_ids` and `regions.list_regions` take
  `retired_only`: the disabled ones alone, paged on their own (the API's new
  `retiredOnly`).

## 0.1.0 — 2026-09-26

First release.

- `AgronextGisClient`: an async client over httpx, one namespace per area of
  the API. It covers every `/api/v1` route except the browser-session
  endpoints (`sign-in`, `sign-out`), plus readiness.
- Typed request and response models ported from the API's schemas. Response
  models ignore unknown fields.
- Its own error hierarchy, built from the API's RFC 9457 problem bodies:
  `code`, `context` and `correlation_id` travel on every `ApiError`.
- `paginate` for paged listings. Geometries are accepted as GeoJSON or
  anything with `__geo_interface__`.
- Contract tests against a snapshot of the API's OpenAPI document.
