# agronext_gis_sdk

**Type: SDK** (§7.4.1). An async Python client for the agronext_gis API:
screening against the socio-environmental registries, rate resolution, the
policy overlap check, and everything behind them (the área catalogue, produtos,
safras, abrangências, rates). Every API call is a method, every answer a typed
model, every failure an error of this package.

Two ways in, and both are public:

- **`gis.underwriting`** follows a SALE: the calls a sale system makes, in the
  order it makes them, each taking what the caller holds at that step.
- **The other namespaces** follow the API, one method per route. They are how
  the catalogue is managed through it: safras, produtos, franquias, rates,
  abrangências, the policy layer.

Runtime dependencies: `httpx` and `pydantic`. It depends on nothing else of
agronext_gis. The API is a service it talks to, never a package it imports.

## Install

From the index, once published:

```bash
uv add agronext-gis-sdk
```

Until then, from a checkout:

```bash
uv add ../agronext_gis/agronext_gis_sdk      # or: uv pip install path/to/agronext_gis_sdk
```

or from a built wheel (`uv build` writes it to `dist/`).

## Use

### A sale: `gis.underwriting`

A buyer knows where they plant, what they plant and what they want to insure
against. They do not know what is sold. Nine calls, in the order a sale makes
them. The first takes nothing; each of the others takes what the sale system
holds at that step and returns what the next one needs — so no id is ever known
in advance or looked up, the safra's included.

```python
import agronext_gis_sdk as gis_sdk


async def sell(gis: gis_sdk.AgronextGisClient, polygons: list[dict]) -> None:
    # 1. the safras being sold today, each with its id: a sale starts here
    open_today = await gis.underwriting.list_open_seasons()
    season = open_today[0]  # the buyer picks, when more than one is open

    # 2. WHERE: only the states with produtos and the municípios with rates
    territory = await gis.underwriting.list_sold_territory(season.id)
    place = territory.states[0].municipalities[0]  # the buyer picks their município

    # 3. WHAT is sold there: each produto with its crop, peril and franquias
    on_sale = await gis.underwriting.list_products_on_sale(season.id, place.municipality_id)
    product = on_sale.products[0]  # the buyer narrows by crop and peril, and picks
    deductible = product.deductibles[0]

    # 4. per polygon, as it is drawn: the CAR imóveis under it, to pick one
    car_codes = []
    for polygon in polygons:
        found = await gis.underwriting.list_car_properties(polygon)
        car_codes.append(found.candidates[0].cod_imovel)  # the buyer picks

    # 5. more than one polygon: may they go in one contract, in that município
    group = await gis.underwriting.validate_group(polygons, municipality_id=place.municipality_id)

    # 6. what it costs: every polygon's rate and the sale's, in ONE request
    try:
        rate = await gis.underwriting.resolve_rates(
            polygons, season_id=season.id, product_id=product.id, deductible_id=deductible.id
        )
    except gis_sdk.PolygonsRefusedError as refused:
        for refusal in refused.refusals:  # every polygon that failed, and why
            print(refusal.polygon_index, refusal.code, refusal.detail)
        return
    print(rate.aggregate_value, rate.aggregate_risk_value, rate.area_ha)
    for item in rate.polygons:
        print(item.polygon_index, item.aggregate_value, item.area_ha, item.run_id)

    # ... the buyer accepts and the purchase is concluded: the sale system's own
    # step. The contract then goes to underwriting, which screens it:

    # 7. the registries on the CAR imóveis picked, by their codes
    screening = await gis.underwriting.screen_car_properties(car_codes)
    # 8. the registries over the polygons themselves
    registries = await gis.underwriting.screen_polygons(polygons)
    # 9. collisions with policies already sold
    overlap = await gis.underwriting.check_policy_overlap(polygons, product_id=product.id)
```

- **A sale starts from `list_open_seasons()`.** A safra is open while today
  falls inside its period. Each carries the `id` every later call takes and the
  `label` a buyer reads; when two are open, the buyer picks.
- **One request per call, however many polygons.** From step 5 on a call takes
  ALL the polygons of the sale; the API does the work per polygon and answers
  per polygon, in the order given. The sale's rate is weighted by area over
  every polygon by the API — there is no arithmetic on the caller's side.
- **The rate is all or nothing.** A polygon that cannot be resolved raises
  `PolygonsRefusedError` and nothing was resolved. Its `refusals` name every
  polygon that failed with the reason (`RateRefusalCode`): ground where the
  produto may not be sold, ground with no rate, a polygon too large.
- **No grid is named.** Each polygon is resolved on the finest grid its size
  allows; its `cell_m` says which. One run is pinned per polygon (`run_id`).
- **The screenings report.** Nothing in their answers is a verdict; whether a
  finding blocks a sale is the sale system's rule.

The API holds the listing behind steps 2 and 3 and refreshes it after the
writes that change what is on sale. Each answer says when (`refreshed_at`). A
place listed there is never a promise of a price: the rate is always resolved
from the rates themselves, so a polygon where selling has just stopped is
refused at step 6.

[`example.py`](example.py) is that sale as a script, and it is how this SDK is
validated against a live API: it walks all nine calls over the network, each
fed by the answers before it, printing the id of everything that can be picked,
and ends `9 calls answered` — or non-zero, saying which request failed or why
it could not go on. See "Develop". It is
also the shape to copy into a sale system: the client as an async generator (a
FastAPI dependency as it stands) and one function per call taking it.

### The API, route by route

Every other namespace follows the API, one method per route — how the catalogue
is managed through it, and what the calls above are built on:

```python
async with gis_sdk.AgronextGisClient(
    base_url="https://gis.example.com",  # the API's root; the client adds /api/v1
    api_key="agx_…",  # a key the API minted for a user
) as gis:
    seasons = await gis.seasons.list_seasons()
    products = await gis.seasons.list_season_products(seasons[0].id)
    # one polygon, with the raster to draw it: which área priced each tile
    answer = await gis.rates.resolve(polygon, product_id=8, deductible_id=13)
    print(answer.aggregate_value, answer.cell_m, len(answer.grid.cells))
```

A geometry is a GeoJSON mapping in EPSG:4326, or anything with
`__geo_interface__` (a shapely geometry, for instance). A produtividade
esperada is always kg/ha: every field carrying one ends in `_kg_ha`.

### The namespaces

| | |
|---|---|
| `gis.underwriting` | a sale, step by step: the safras open today, what is on sale where, the CAR imóveis under a polygon, the group check, the rate, and the three screenings of a contract |
| `gis.access` | the caller (`me`), and for an admin: users, keys, the audit trail |
| `gis.geography` | Brazil, UFs, municípios; `locate` a geometry |
| `gis.screening` | CAR imóveis over an area, registry findings by CAR code, registry features over one polygon or several, pinned runs |
| `gis.areas` / `gis.regions` | the catálogo of áreas and named sets of them |
| `gis.products` | produtos and their franquias |
| `gis.seasons` | safras, the produtos each sells, copying produtos between safras, where each safra has anything on sale |
| `gis.pairs` | one (safra, produto): abrangência, fatores, planting windows, bonificações/agravamentos, overlap order |
| `gis.rates` | rates written, their trail, `resolve` (one polygon) and `resolve_polygons` (a sale's), `heatmap`, runs, refreshing the on-sale listing |
| `gis.policies` | the policy layer and the overlap check, for one polygon or several |
| `gis.groups` | the distance check between polygons |
| `gis.tools` | KML import/export, measuring a polygon |

`gis.ready()` answers the API's readiness probe.

Request bodies are this package's request models, and path and query parameters
are keyword arguments. Paged listings return `Page[T]`. `paginate` walks every
page for you:

```python
async for area in gis_sdk.paginate(gis.areas.list_areas, level=gis_sdk.LayerLevel.STATE):
    ...
```

### Errors

Everything raised is a `gis_sdk.AgronextGisError`:

- `ApiError`: the API answered with an error. Branch on `code`, the API's
  stable machine code (`rates.copy.windows_undeclared`), not on the wording.
  `context` holds the rejection's own fields, `errors` a validation failure's
  per-field issues, and `correlation_id` the id the API logged it under.
  There are subclasses by status: `UnauthorizedError` (401), `ForbiddenError`
  (403), `NotFoundError` (404), `ConflictError` (409), `UnprocessableError`
  (422) and `ServerError` (5xx).
- `PolygonsRefusedError`, an `UnprocessableError`: the rate of a sale was asked
  and at least one polygon cannot be resolved, so none was. `refusals` holds,
  per polygon that failed, its `polygon_index`, the `code` of the reason
  (`RateRefusalCode`), the `detail` in words and the reason's own `context` —
  how much of the polygon, and where.
- `TransportError`: no answer at all (refused, reset, timed out).
- `ResponseMismatchError`: an answer this version of the SDK cannot read.

```python
try:
    await gis.seasons.set_season_products(season_id, request)
except gis_sdk.UnprocessableError as refused:
    if refused.code == "rates.copy.windows_undeclared":
        missing = refused.context["undeclared_product_ids"]
```

The SDK logs nothing above DEBUG (logger `agronext_gis_sdk`). What an error is
worth is the caller's call.

### Settings

All of them go to the constructor. The SDK reads no environment.

| | |
|---|---|
| `base_url`, `api_key` | required |
| `timeout` | seconds per request, 30 by default; set once, applies to every call |
| `ca_bundle` | a private CA's certificates. TLS is always verified, and there is no switch to turn that off |
| `connect_retries` | retries of a connection that could not be ESTABLISHED (2); a request that got an answer is never retried |
| `request_id`, `request_id_header` | a callable returning your correlation id, sent in `request_id_header` (`X-Request-ID` by default; the local stack renames it `X-Correlation-ID` via `API_CORRELATION_ID_HEADER`). A UUID is ADOPTED by the API as its own id for the request |
| `transport` | replaces the network: `httpx.MockTransport` in tests, `httpx.ASGITransport(app=...)` to run against an API in the same process |

## Keeping it in step with the API

The models are this package's own, ported from the API's schemas. Response
models ignore fields they do not know, so an API that grows a field never
breaks a caller on an older SDK.

`tests/openapi.json` is a snapshot of the API's OpenAPI document, and
`tests/test_contract.py` checks the SDK against it. It fails on:

- an API route no method calls;
- a query parameter or body member the route does not read;
- a model whose fields differ from the API schema it mirrors, or that requires
  a field the API may leave out;
- an enum whose values differ.

After changing the API:

```bash
cd agronext_gis_api
uv run python ../agronext_gis_sdk/scripts/refresh_openapi.py
cd ../agronext_gis_sdk && uv run pytest
```

## Develop

```bash
uv sync
uv run pytest            # unit + contract, no services needed
uv run mypy              # strict
uv run ruff check && uv run ruff format --check
uv build                 # the wheel, in dist/
```

The tests stub the API at the HTTP boundary, so they pin what the SDK sends and
how it reads an answer — not whether a real API agrees. That is `example.py`,
run against one:

```bash
uv run --env-file ../.env python example.py                 # the safra open today
uv run --env-file ../.env python example.py --season-id 8   # one safra, by its id
uv run --env-file ../.env python example.py --help
```

It reads `GIS_BASE_URL` (the API's root) and `GIS_API_KEY` (the key of a calling
system registered there) — the `GIS_*` block of the project's `.env.example`.
Nobody needs an id in advance: the run prints the open safras first, and then
the id of each thing an option can name, before picking from it.
Exit 0 is all nine calls answered; 2 is a run that could not go on, with the
reason; 1 is a request that failed, named. It lives
beside `src/` and is in no wheel: `typer` and `pydantic-settings`, which it
needs, are development dependencies.

Semantic versioning (§7.2): a breaking change to a method or model is a major
version. See `CHANGELOG.md`.
