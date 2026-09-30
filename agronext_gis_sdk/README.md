# agronext_gis_sdk

**Type: SDK** (§7.4.1). An async Python client for the agronext_gis API:
screening against the socio-environmental registries, rate resolution, the
policy overlap check, and everything behind them (the área catalogue, produtos,
safras, abrangências, rates). Every API call is a method, every answer a typed
model, every failure an error of this package.

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

```python
import asyncio

import agronext_gis_sdk as gis_sdk


async def resolve_area(polygon: dict) -> None:
    async with gis_sdk.AgronextGisClient(
        base_url="https://gis.example.com",  # the API's root; the client adds /api/v1
        api_key="agx_…",  # a key the API minted for a user
    ) as gis:
        # 1. distance check between the policy's polygons
        group = await gis.groups.validate([polygon])
        # 2. collision with a running policy
        overlap = await gis.policies.check_overlap(
            gis_sdk.PolicyOverlapRequest(geometry=polygon, product_id=8)
        )
        # 3. what the registries say about the CAR imóveis there
        candidates = await gis.screening.preflight(polygon)
        # 4. the rate and the expected yield: per tile and area-weighted,
        #    pinned as a run
        options = await gis.rates.preflight(polygon)
        answer = await gis.rates.resolve(
            polygon, product_id=8, deductible_id=2, cell_m=options.recommended_cell_m
        )
        print(answer.aggregate_value, answer.aggregate_risk_value, answer.run_id)
        print(answer.aggregate_expected_yield_kg_ha)  # None unless every tile has one


asyncio.run(resolve_area({"type": "Polygon", "coordinates": [[...]]}))
```

A sale system's whole integration is in [`example.py`](example.py). It covers
Triagem (group, CAR imóveis, CAR screening, the plot's ESG, policy collisions)
and Resolver ("À venda", the rate per plot and over the policy), with the client
as a FastAPI dependency.

A geometry is a GeoJSON mapping in EPSG:4326, or anything with
`__geo_interface__` (a shapely geometry, for instance). A produtividade
esperada is always kg/ha: every field carrying one ends in `_kg_ha`.

### The namespaces

| | |
|---|---|
| `gis.access` | the caller (`me`), and for an admin: users, keys, the audit trail |
| `gis.geography` | Brazil, UFs, municípios; `locate` a geometry |
| `gis.screening` | CAR imóveis over an area, registry findings, pinned runs |
| `gis.areas` / `gis.regions` | the catálogo of áreas and named sets of them |
| `gis.products` | produtos and their franquias |
| `gis.seasons` | safras, the produtos each sells, copying produtos between safras |
| `gis.pairs` | one (safra, produto): abrangência, fatores, planting windows, bonificações/agravamentos, overlap order |
| `gis.rates` | rates written, their trail, `resolve`, `heatmap`, runs |
| `gis.policies` | the policy layer and the overlap check |
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

Semantic versioning (§7.2): a breaking change to a method or model is a major
version. See `CHANGELOG.md`.
