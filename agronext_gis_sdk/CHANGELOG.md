# Changelog

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
