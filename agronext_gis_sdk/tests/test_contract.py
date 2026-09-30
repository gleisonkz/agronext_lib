"""The SDK against the API's own OpenAPI document (`openapi.json`, a snapshot).

Refresh the snapshot with `scripts/refresh_openapi.py` whenever the API changes;
these tests then name everything the SDK no longer matches:

- a route of the API that no SDK method calls (or one that calls a route the
  API does not have);
- a query parameter the SDK sends that the route does not read — which is how a
  camelCase/snake_case slip would otherwise pass silently;
- a JSON body member the route's request schema does not declare;
- a model whose fields differ from the API schema it mirrors, or that REQUIRES a
  field the API may leave out;
- an enum whose values differ.
"""

import datetime
import decimal
import enum
import json
import re
from collections.abc import Awaitable, Callable, Iterator, Mapping
from pathlib import Path
from typing import Any, Final

import httpx
import pydantic
import pytest

import agronext_gis_sdk as sdk
from agronext_gis_sdk import AgronextGisClient

from .conftest import Recorder, client_for

SPEC: Final[dict[str, Any]] = json.loads((Path(__file__).parent / "openapi.json").read_text())
COMPONENTS: Final[dict[str, Any]] = SPEC["components"]["schemas"]

#: Routes the SDK deliberately does not wrap: browser sessions (a key-holding
#: caller has no use for a cookie), the browser's boot configuration, and bare
#: liveness (the SDK wraps readiness).
NOT_WRAPPED: Final[frozenset[tuple[str, str]]] = frozenset(
    {
        ("POST", "/api/v1/access/sign-in"),
        ("POST", "/api/v1/access/sign-out"),
        ("GET", "/config"),
        ("GET", "/health"),
    }
)

#: API schemas that are not models on the SDK side: array envelopes (the SDK
#: returns `list[...]`), the generic page (checked against `Page`), multipart
#: bodies, the sign-in form, the browser config, liveness, and FastAPI's own.
NOT_MODELLED: Final[re.Pattern[str]] = re.compile(
    r"^(Catalogue_.*|Page_.*|Body_.*|StateList|MunicipalityList|SnapshotReferenceList"
    r"|SignInRequest|RuntimeConfigResponse|LivenessResponse|HTTPValidationError"
    r"|ValidationError)$"
)

#: API schema names the SDK spells differently, because two API apps each
#: declare a schema of that name and the SDK has ONE namespace.
RENAMED: Final[Mapping[str, str]] = {
    "agronext_gis_api__apps__rates__schemas__SeasonItem": "SeasonItem",
    "agronext_gis_api__apps__rates__schemas__PlantingWindowItem": "PlantingWindowItem",
    "agronext_gis_api__apps__policies__schemas__SeasonItem": "PolicySeasonItem",
    "agronext_gis_api__apps__policies__schemas__PlantingWindowItem": "PolicyPlantingWindowItem",
    "agronext_gis_api__apps__groups__schemas__PolygonSummary": "GroupPolygonSummary",
    "agronext_gis_api__apps__client_tools__schemas__PolygonSummary": "PolygonSummary",
    "BrazilianStates": "BrazilianState",
}

POINT: Final[dict[str, Any]] = {"type": "Point", "coordinates": [-47.9, -15.8]}
D = decimal.Decimal

type Call = Callable[[AgronextGisClient], Awaitable[object]]

#: One call per SDK method, with the arguments that exercise its query string.
CALLS: Final[Mapping[str, Call]] = {
    "ready": lambda gis: gis.ready(),
    # access
    "me": lambda gis: gis.access.me(),
    "rotate_my_key": lambda gis: gis.access.rotate_my_key(),
    "list_users": lambda gis: gis.access.list_users(page=2, size=10),
    "create_user": lambda gis: gis.access.create_user(
        sdk.CreateUserRequest(username="svc", with_password=False)
    ),
    "set_user_access": lambda gis: gis.access.set_user_access(
        7, sdk.UpdateAccessRequest(is_admin=False, can_write=True, is_active=True)
    ),
    "reset_password": lambda gis: gis.access.reset_password(7),
    "rotate_user_key": lambda gis: gis.access.rotate_user_key(7),
    "list_changes": lambda gis: gis.access.list_changes(
        entity="seasons", entity_id="1", actor_user_id=2, page=1, size=5
    ),
    # geography
    "country": lambda gis: gis.geography.country(),
    "list_states": lambda gis: gis.geography.list_states(include_geometry=True),
    "get_state": lambda gis: gis.geography.get_state(12),
    "list_state_municipalities": lambda gis: gis.geography.list_state_municipalities(12),
    "list_municipalities": lambda gis: gis.geography.list_municipalities(
        query="Rio", state_id=12, page=1, size=5
    ),
    "get_municipality": lambda gis: gis.geography.get_municipality(120),
    "locate": lambda gis: gis.geography.locate(POINT),
    # screening
    "preflight": lambda gis: gis.screening.preflight(POINT, limit=10),
    "screen": lambda gis: gis.screening.screen(
        sdk.ScreeningRequest(items=[sdk.ScreeningItemRequest(cod_imovel="AC-1")])
    ),
    "list_sources": lambda gis: gis.screening.list_sources(
        kind=sdk.RegistryKind.RESTRICTION, state=sdk.BrazilianState.AC
    ),
    "coverage_statement": lambda gis: gis.screening.coverage_statement(
        as_of=datetime.datetime(2026, 1, 1, tzinfo=datetime.UTC)
    ),
    "overlaps": lambda gis: gis.screening.overlaps(POINT, limit=5),
    "list_screening_runs": lambda gis: gis.screening.list_runs(
        kind=sdk.RunKind.SCREENING, user_id=2, page=1, size=5
    ),
    "get_screening_run": lambda gis: gis.screening.get_run(3),
    # areas and regions
    "list_areas": lambda gis: gis.areas.list_areas(
        level=sdk.LayerLevel.CAR,
        levels=[sdk.LayerLevel.STATE, sdk.LayerLevel.MUNICIPALITY],
        state_id=12,
        municipality_id=120,
        query="x",
        ids=[1, 2],
        include_retired=True,
        retired_only=True,
        page=1,
        size=5,
    ),
    "list_area_ids": lambda gis: gis.areas.list_area_ids(
        level=sdk.LayerLevel.CUSTOM, state_id=12, query="x", ids=[1], include_retired=True
    ),
    "get_area": lambda gis: gis.areas.get_area(5),
    "create_area": lambda gis: gis.areas.create_area("A", POINT, code="A-1"),
    "update_area": lambda gis: gis.areas.update_area(5, sdk.CustomAreaUpdateRequest(name="B")),
    "retire_area": lambda gis: gis.areas.retire_area(5),
    "area_usage": lambda gis: gis.areas.area_usage(5),
    "list_area_revisions": lambda gis: gis.areas.list_area_revisions(5, page=1, size=5),
    "list_regions": lambda gis: gis.regions.list_regions(
        include_retired=True, retired_only=True, folder_id=2, unfiled=False, page=1, size=5
    ),
    "list_folders": lambda gis: gis.regions.list_folders(),
    "create_folder": lambda gis: gis.regions.create_folder("Pera"),
    "rename_folder": lambda gis: gis.regions.rename_folder(2, "Pera 2"),
    "delete_folder": lambda gis: gis.regions.delete_folder(2),
    "create_region": lambda gis: gis.regions.create_region(
        sdk.RegionCreateRequest(name="Sul", area_level=sdk.LayerLevel.MUNICIPALITY, area_ids=[1])
    ),
    "get_region": lambda gis: gis.regions.get_region(4),
    "update_region": lambda gis: gis.regions.update_region(
        4, sdk.RegionUpdateRequest(name="Sul", code="S", folder_id=2)
    ),
    "set_region_areas": lambda gis: gis.regions.set_region_areas(4, [1, 2]),
    "retire_region": lambda gis: gis.regions.retire_region(4),
    # products
    "list_products": lambda gis: gis.products.list_products(include_retired=True),
    "create_product": lambda gis: gis.products.create_product(
        sdk.ProductCreateRequest(code="PERA")
    ),
    "update_product": lambda gis: gis.products.update_product(
        8, sdk.ProductUpdateRequest(name="Pera")
    ),
    "retire_product": lambda gis: gis.products.retire_product(8),
    "list_product_seasons": lambda gis: gis.products.list_product_seasons(8, include_retired=True),
    "list_deductibles": lambda gis: gis.products.list_deductibles(8, include_retired=True),
    "create_deductible": lambda gis: gis.products.create_deductible(
        8, sdk.DeductibleCreateRequest(value=D("0.20"))
    ),
    "retire_deductible": lambda gis: gis.products.retire_deductible(2),
    # seasons
    "list_seasons": lambda gis: gis.seasons.list_seasons(include_retired=True),
    "list_open_seasons": lambda gis: gis.seasons.list_open_seasons(),
    "latest_season": lambda gis: gis.seasons.latest_season(),
    "create_season": lambda gis: gis.seasons.create_season(
        sdk.SeasonCreateRequest(
            label="2027/2028",
            product_ids=[8],
            copies=[sdk.ProductCopyDeclaration(product_id=8, from_season_id=1, windows=[])],
        )
    ),
    "update_season": lambda gis: gis.seasons.update_season(
        1, sdk.SeasonUpdateRequest(label="2027/2028")
    ),
    "retire_season": lambda gis: gis.seasons.retire_season(1),
    "list_season_products": lambda gis: gis.seasons.list_season_products(1, include_retired=True),
    "set_season_products": lambda gis: gis.seasons.set_season_products(
        1, sdk.SeasonProductsRequest(product_ids=[8])
    ),
    # pairs
    "configuration": lambda gis: gis.pairs.configuration(1, 8),
    "list_planting_windows": lambda gis: gis.pairs.list_planting_windows(
        1, 8, include_retired=True
    ),
    "set_planting_windows": lambda gis: gis.pairs.set_planting_windows(1, 8, []),
    "pricing": lambda gis: gis.pairs.pricing(1, 8),
    "set_pricing": lambda gis: gis.pairs.set_pricing(
        1, 8, sdk.PricingRequest(mode=sdk.RateMode.RATIO)
    ),
    "list_adjustments": lambda gis: gis.pairs.list_adjustments(
        1, 8, state_id=12, query="AC", page=1, size=5
    ),
    "write_adjustments": lambda gis: gis.pairs.write_adjustments(
        1,
        8,
        sdk.CarAdjustmentBatchRequest(
            operations=[sdk.CarAdjustmentOperationRequest(area_id=3, percent=D("10"))]
        ),
    ),
    "list_adjustment_history": lambda gis: gis.pairs.list_adjustment_history(1, 8, page=1, size=5),
    "scope": lambda gis: gis.pairs.scope(1, 8),
    "save_scope": lambda gis: gis.pairs.save_scope(1, 8, sdk.ScopeRequest(allowed_area_ids=[1])),
    "preview_scope": lambda gis: gis.pairs.preview_scope(
        1, 8, sdk.ScopeRequest(allowed_area_ids=[1])
    ),
    "list_scope_areas": lambda gis: gis.pairs.list_scope_areas(
        1, 8, level=sdk.LayerLevel.CAR, state_id=12, query="x", ids=[1], page=1, size=5
    ),
    "scope_outline": lambda gis: gis.pairs.scope_outline(
        1, 8, region_id=5, state_id=12, level=sdk.LayerLevel.MUNICIPALITY
    ),
    "scope_summary": lambda gis: gis.pairs.scope_summary(1, 8, state_id=12),
    "territory": lambda gis: gis.pairs.territory(1, 8),
    "list_contests": lambda gis: gis.pairs.list_contests(1, 8),
    "order_contest": lambda gis: gis.pairs.order_contest(1, 8, 2, [5, 4]),
    # rates
    "list_rates": lambda gis: gis.rates.list_rates(
        product_id=8,
        season_id=1,
        reference=True,
        level=sdk.LayerLevel.MUNICIPALITY,
        area_id=3,
        state_id=12,
        page=1,
        size=5,
    ),
    "coverage": lambda gis: gis.rates.coverage(season_id=1, product_id=8, deductible_id=2),
    "write": lambda gis: gis.rates.write(
        sdk.RateWriteBatchRequest(
            operations=[
                sdk.RateWriteOperationRequest(
                    season_id=1,
                    product_id=8,
                    deductible_id=None,
                    area_id=3,
                    value=D("10.5"),
                    risk_value=D("2"),
                )
            ]
        )
    ),
    "list_writes": lambda gis: gis.rates.list_writes(
        season_id=1,
        product_id=8,
        deductible_id=2,
        area_id=3,
        user_id=2,
        batch_id=9,
        page=1,
        size=5,
    ),
    "list_write_batches": lambda gis: gis.rates.list_write_batches(
        user_id=2, season_id=1, product_id=8, reference=True, page=1, size=5
    ),
    "rates_preflight": lambda gis: gis.rates.preflight(POINT, cell_m=100),
    "resolve": lambda gis: gis.rates.resolve(POINT, product_id=8, deductible_id=2, cell_m=100),
    "heatmap": lambda gis: gis.rates.heatmap(
        sdk.RateHeatmapRequest(
            product_id=8, deductible_id=2, cell_m=250, bbox=(-50.0, -30.0, -45.0, -25.0)
        )
    ),
    "list_rate_runs": lambda gis: gis.rates.list_runs(
        user_id=2, season_id=1, product_id=8, deductible_id=2, page=1, size=5
    ),
    "get_rate_run": lambda gis: gis.rates.get_run(4),
    # policies
    "check_overlap": lambda gis: gis.policies.check_overlap(
        sdk.PolicyOverlapRequest(geometry=POINT, product_id=8)
    ),
    "list_policy_areas": lambda gis: gis.policies.list_policy_areas(
        season_id=1,
        product_id=8,
        policy_id="P-1",
        running_only=False,
        planting_window_id=3,
        unwindowed_only=True,
        include_geometry=True,
        page=1,
        size=5,
    ),
    "list_loads": lambda gis: gis.policies.list_loads(season_id=1, page=1, size=5),
    "load": lambda gis: gis.policies.load(
        sdk.PolicyLoadRequest(
            season_id=1, product_id=8, areas=[sdk.PolicyAreaInput(policy_id="P", geometry=POINT)]
        )
    ),
    "stand_down": lambda gis: gis.policies.stand_down(6),
    "delete_policy_area": lambda gis: gis.policies.delete_policy_area(6),
    # groups and tools
    "validate": lambda gis: gis.groups.validate([POINT, POINT]),
    "import_kml_polygon": lambda gis: gis.tools.import_kml_polygon(b"<kml/>"),
    "import_kml_polygons": lambda gis: gis.tools.import_kml_polygons(b"<kml/>"),
    "export_kml": lambda gis: gis.tools.export_kml(
        sdk.KmlExportRequest(polygons=[sdk.NamedPolygonRequest(geometry=POINT)])
    ),
    "summarise_polygon": lambda gis: gis.tools.summarise_polygon(POINT),
}


def _operations() -> Iterator[tuple[str, str, re.Pattern[str], dict[str, Any]]]:
    for path, operations in SPEC["paths"].items():
        pattern = re.compile("^" + re.sub(r"\{[^/]+\}", "[^/]+", path) + "$")
        for method, operation in operations.items():
            yield method.upper(), path, pattern, operation


def _refused(request: httpx.Request) -> httpx.Response:
    """Every call ends in a refusal: the request is what is under test here."""
    return httpx.Response(599, json={"detail": "recorded", "code": "test.recorded"})


async def _record(name: str) -> httpx.Request:
    recorder = Recorder(_refused)
    async with client_for(recorder) as gis:
        with pytest.raises(sdk.ApiError):
            await CALLS[name](gis)
    [request] = recorder.requests
    return request


def _operation_for(request: httpx.Request) -> tuple[str, dict[str, Any]]:
    for method, path, pattern, operation in _operations():
        if method == request.method and pattern.match(request.url.path):
            return path, operation
    pytest.fail(f"{request.method} {request.url.path} is not a route of the API")


def _schema(reference: Mapping[str, Any]) -> dict[str, Any]:
    ref = reference.get("$ref")
    return COMPONENTS[ref.rsplit("/", 1)[-1]] if isinstance(ref, str) else dict(reference)


# --------------------------------------------------------------------------- #
# Routes, query strings and bodies
# --------------------------------------------------------------------------- #


async def test_every_route_of_the_api_is_wrapped_by_exactly_the_calls_above() -> None:
    covered = set()
    for name in CALLS:
        request = await _record(name)
        path, _ = _operation_for(request)
        covered.add((request.method, path))
    every = {(method, path) for method, path, _, _ in _operations()}
    assert every - NOT_WRAPPED - covered == set(), "API routes no SDK method calls"
    assert covered & NOT_WRAPPED == set()


@pytest.mark.parametrize("name", sorted(CALLS))
async def test_the_query_string_names_only_parameters_the_route_reads(name: str) -> None:
    request = await _record(name)
    _, operation = _operation_for(request)
    declared = {p["name"] for p in operation.get("parameters", []) if p["in"] == "query"}
    sent = set(request.url.params.keys())
    assert sent <= declared, f"{name} sends {sorted(sent - declared)}"


@pytest.mark.parametrize("name", sorted(CALLS))
async def test_the_body_carries_only_members_the_route_declares(name: str) -> None:
    request = await _record(name)
    _, operation = _operation_for(request)
    content = operation.get("requestBody", {}).get("content", {})
    if "multipart/form-data" in content:
        fields = set(_schema(content["multipart/form-data"]["schema"])["properties"])
        assert b'name="file"' in request.content and "file" in fields
        return
    if not request.content:
        assert "application/json" not in content or not operation["requestBody"].get("required")
        return
    declared = set(_schema(content["application/json"]["schema"])["properties"])
    sent = set(json.loads(request.content))
    assert sent <= declared, f"{name} sends {sorted(sent - declared)}"


# --------------------------------------------------------------------------- #
# Models and enums
# --------------------------------------------------------------------------- #


def _sdk_models() -> dict[str, type[pydantic.BaseModel]]:
    return {
        name: value
        for name in sdk.__all__
        if isinstance(value := getattr(sdk, name), type) and issubclass(value, pydantic.BaseModel)
    }


def _sdk_enums() -> dict[str, type[enum.Enum]]:
    return {
        name: value
        for name in sdk.__all__
        if isinstance(value := getattr(sdk, name), type) and issubclass(value, enum.Enum)
    }


def _api_objects() -> Iterator[tuple[str, dict[str, Any]]]:
    for name, schema in COMPONENTS.items():
        if "properties" in schema and not NOT_MODELLED.match(name):
            yield RENAMED.get(name, name), schema


@pytest.mark.parametrize(("name", "schema"), list(_api_objects()), ids=lambda v: str(v)[:40])
def test_every_api_schema_has_a_model_with_the_same_fields(
    name: str, schema: dict[str, Any]
) -> None:
    model = _sdk_models().get(name)
    assert model is not None, f"the SDK has no model for the API's {name}"
    aliases = {field.alias or field_name for field_name, field in model.model_fields.items()}
    assert aliases == set(schema["properties"]), f"{name}: fields differ"
    required = {field.alias for field in model.model_fields.values() if field.is_required()}
    assert required <= set(schema.get("required", [])), f"{name} requires what the API may omit"


def test_the_page_envelope_matches_the_apis() -> None:
    page = COMPONENTS["Page_AreaItem_"]
    assert set(sdk.Page[sdk.AreaItem].model_fields) == set(page["properties"])


@pytest.mark.parametrize(
    ("name", "schema"),
    [(RENAMED.get(n, n), s) for n, s in COMPONENTS.items() if "enum" in s],
)
def test_every_api_enum_has_the_same_values(name: str, schema: dict[str, Any]) -> None:
    member = _sdk_enums().get(name)
    assert member is not None, f"the SDK has no enum for the API's {name}"
    assert [item.value for item in member] == schema["enum"]
