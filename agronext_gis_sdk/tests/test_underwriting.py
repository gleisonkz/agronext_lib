"""`gis.underwriting`: the calls of a sale, each on the route that owns it.

What is pinned: the request each call sends — ONE per call, however many
polygons the sale has — the typed answer it returns, and that what the API
refuses is the SDK's own error, never an empty answer.
"""

import datetime
import decimal
import json
from typing import Any

import httpx
import pytest

import agronext_gis_sdk as sdk

from .conftest import Recorder, client_for

D = decimal.Decimal


def _square(lon: float, lat: float, side: float = 0.004) -> dict[str, Any]:
    half = side / 2
    ring = [
        [lon - half, lat - half],
        [lon + half, lat - half],
        [lon + half, lat + half],
        [lon - half, lat + half],
        [lon - half, lat - half],
    ]
    return {"type": "Polygon", "coordinates": [ring]}


FIRST = _square(-50.87, -27.03)
SECOND = _square(-50.80, -27.03)

SNAPSHOT = {
    "sourceKey": "sicar",
    "label": "SICAR",
    "authority": "SFB",
    "kind": "registry",
    "snapshotId": 31,
    "fetchedAt": "2026-09-01",
    "ageDays": 42,
    "stale": False,
}
LAYER = {
    "index": 0,
    "areaId": 42,
    "level": "municipality",
    "name": "Fraiburgo",
    "rank": 1,
    "value": "11.770000",
    "riskValue": "13.120000",
    "tileCount": 1849,
    "areaHa": 17.6,
    "sharePct": 100.0,
}

TERRITORY = {
    "seasonId": 3,
    "refreshedAt": "2026-10-13T14:30:00Z",
    "states": [
        {
            "stateId": 42,
            "abbr": "SC",
            "name": "Santa Catarina",
            "municipalities": [
                {"municipalityId": 4205506, "name": "Fraiburgo"},
                {"municipalityId": 4200408, "name": "Água Doce"},
            ],
        }
    ],
}
ON_SALE = {
    "seasonId": 3,
    "municipalityId": 4205506,
    "refreshedAt": "2026-10-13T14:30:00Z",
    "products": [
        {
            "id": 8,
            "code": "PERA",
            "name": "Pera",
            "crop": "Pera",
            "peril": "Granizo",
            "deductibles": [
                {"id": 13, "productId": 8, "value": "0.2000", "retiredAt": None},
                {"id": 14, "productId": 8, "value": "0.2500", "retiredAt": None},
            ],
        }
    ],
}


OPEN_SEASONS = [
    {
        "id": 3,
        "label": "2026/2027",
        "ordinal": 3,
        "isLatest": True,
        "startsOn": "2026-07-01",
        "endsOn": "2027-06-30",
        "isOpen": True,
        "retiredAt": None,
        "productCount": 2,
    }
]


def _answer(status: int, body: object) -> Recorder:
    return Recorder(lambda request: httpx.Response(status, json=body))


async def test_a_sale_starts_from_the_safras_open_today_and_takes_nothing() -> None:
    recorder = _answer(200, OPEN_SEASONS)
    async with client_for(recorder) as gis:
        open_today = await gis.underwriting.list_open_seasons()

    [request] = recorder.requests
    assert (request.method, request.url.path) == ("GET", "/api/v1/rates/seasons/open")
    assert not request.url.params
    assert not request.content
    [season] = open_today
    # The id every later call takes, the label a buyer reads, and its period.
    assert (season.id, season.label) == (3, "2026/2027")
    assert (season.starts_on, season.ends_on) == (
        datetime.date(2026, 7, 1),
        datetime.date(2027, 6, 30),
    )
    assert season.is_open


async def test_no_safra_open_today_is_an_empty_list() -> None:
    async with client_for(_answer(200, [])) as gis:
        assert await gis.underwriting.list_open_seasons() == []


async def test_where_anything_is_on_sale_is_one_request_for_the_safra() -> None:
    recorder = _answer(200, TERRITORY)
    async with client_for(recorder) as gis:
        territory = await gis.underwriting.list_sold_territory(3)

    [request] = recorder.requests
    assert (request.method, request.url.path) == ("GET", "/api/v1/rates/seasons/3/territory")
    assert not request.content
    [state] = territory.states
    assert (state.state_id, state.abbr, state.name) == (42, "SC", "Santa Catarina")
    assert [(place.municipality_id, place.name) for place in state.municipalities] == [
        (4205506, "Fraiburgo"),
        (4200408, "Água Doce"),
    ]
    assert territory.refreshed_at == datetime.datetime(2026, 10, 13, 14, 30, tzinfo=datetime.UTC)


async def test_a_listing_that_holds_nothing_has_no_states_and_no_date() -> None:
    async with client_for(_answer(200, {"seasonId": 3, "refreshedAt": None, "states": []})) as gis:
        territory = await gis.underwriting.list_sold_territory(3)
    assert territory.states == []
    assert territory.refreshed_at is None


async def test_what_is_on_sale_in_a_municipality_is_one_request_by_its_ibge_code() -> None:
    recorder = _answer(200, ON_SALE)
    async with client_for(recorder) as gis:
        on_sale = await gis.underwriting.list_products_on_sale(3, 4205506)

    [request] = recorder.requests
    assert (request.method, request.url.path) == (
        "GET",
        "/api/v1/rates/seasons/3/municipalities/4205506/products",
    )
    [product] = on_sale.products
    assert (product.id, product.code, product.crop, product.peril) == (
        8,
        "PERA",
        "Pera",
        "Granizo",
    )
    # What pricing a polygon takes next: the ids, with the values to show.
    assert [(franquia.id, franquia.value) for franquia in product.deductibles] == [
        (13, D("0.2000")),
        (14, D("0.2500")),
    ]


async def test_nothing_on_sale_there_is_an_empty_list() -> None:
    body: dict[str, object] = {
        "seasonId": 3,
        "municipalityId": 1100015,
        "refreshedAt": None,
        "products": [],
    }
    async with client_for(_answer(200, body)) as gis:
        on_sale = await gis.underwriting.list_products_on_sale(3, 1100015)
    assert on_sale.products == []


async def test_a_municipality_that_does_not_exist_is_an_error_not_an_empty_answer() -> None:
    problem = {
        "type": "urn:problem-type:resource.not_found",
        "title": "Not Found",
        "status": 404,
        "detail": "municipality 9999999 does not exist",
        "code": "resource.not_found",
        "correlationId": "c0ffee",
        "municipality_id": 9999999,
    }
    async with client_for(_answer(404, problem)) as gis:
        with pytest.raises(sdk.NotFoundError) as raised:
            await gis.underwriting.list_products_on_sale(3, 9999999)
    assert raised.value.code == "resource.not_found"
    assert raised.value.context == {"municipality_id": 9999999}


async def test_the_route_level_calls_are_the_same_requests() -> None:
    """`gis.underwriting` owns no path: it calls the method that does."""
    recorder = Recorder(
        lambda request: httpx.Response(
            200, json=ON_SALE if "municipalities" in request.url.path else TERRITORY
        )
    )
    async with client_for(recorder) as gis:
        await gis.underwriting.list_sold_territory(3)
        await gis.seasons.list_sold_territory(3)
        await gis.underwriting.list_products_on_sale(3, 4205506)
        await gis.seasons.list_products_on_sale(3, 4205506)

    first, second, third, fourth = recorder.requests
    assert (first.method, first.url) == (second.method, second.url)
    assert (third.method, third.url) == (fourth.method, fourth.url)


async def test_a_forced_refresh_is_a_post_with_no_body() -> None:
    recorder = _answer(200, {"refreshedAt": "2026-10-13T14:30:00Z"})
    async with client_for(recorder) as gis:
        refreshed = await gis.rates.refresh_sold_territory()

    [request] = recorder.requests
    assert (request.method, request.url.path) == ("POST", "/api/v1/rates/territory/refresh")
    assert not request.content
    assert refreshed.refreshed_at == datetime.datetime(2026, 10, 13, 14, 30, tzinfo=datetime.UTC)


# --------------------------------------------------------------------------- #
# While the polygons are drawn
# --------------------------------------------------------------------------- #

CAR_PROPERTIES = {
    "total": 1,
    "candidates": [
        {
            "areaId": 501,
            "codImovel": "SC-4205506-0001",
            "status": "AT",
            "statusLabel": "Ativo",
            "areaHa": 120.0,
            "municipalityId": 4205506,
            "municipality": "Fraiburgo",
            "state": "SC",
            "overlapHa": 12.5,
            "overlapPct": 71.0,
            "geometry": FIRST,
        }
    ],
    "carSnapshot": SNAPSHOT,
}


async def test_the_car_properties_under_a_polygon_are_one_request_for_that_polygon() -> None:
    recorder = _answer(200, CAR_PROPERTIES)
    async with client_for(recorder) as gis:
        found = await gis.underwriting.list_car_properties(FIRST)

    [request] = recorder.requests
    assert (request.method, request.url.path) == ("POST", "/api/v1/screening/preflight")
    assert json.loads(request.content) == {"geometry": FIRST, "limit": None}
    [candidate] = found.candidates
    # The code the CAR screening takes, and how much of the polygon it covers.
    assert (candidate.cod_imovel, candidate.overlap_pct) == ("SC-4205506-0001", 71.0)
    assert found.car_snapshot.snapshot_id == 31


GROUP = {
    "valid": False,
    "errors": ["polygon 2 has no vertex in Fraiburgo"],
    "warnings": [],
    "polygons": [],
    "pairs": [],
    "sharedMunicipality": None,
    "centroid": [-50.83, -27.03],
    "totalAreaHa": 35.2,
    "thresholds": {
        "okDistanceKm": 3.0,
        "maxDistanceKm": 20.0,
        "maxPolygons": 12,
        "minSharedMunicipalityPct": 50.0,
    },
}


async def test_a_group_is_checked_in_the_municipality_the_sale_is_in() -> None:
    recorder = _answer(200, GROUP)
    async with client_for(recorder) as gis:
        verdict = await gis.underwriting.validate_group(
            [FIRST, SECOND], municipality_id=4205506, min_shared_municipality_pct=50.0
        )

    [request] = recorder.requests
    assert (request.method, request.url.path) == ("POST", "/api/v1/groups/validate")
    assert json.loads(request.content) == {
        "geometries": [FIRST, SECOND],
        "municipalityId": 4205506,
        "minSharedMunicipalityPct": 50.0,
    }
    # A group that fails a rule is an answer, not an error.
    assert verdict.valid is False
    assert verdict.errors == ["polygon 2 has no vertex in Fraiburgo"]
    assert verdict.thresholds.min_shared_municipality_pct == 50.0


# --------------------------------------------------------------------------- #
# What the sale costs
# --------------------------------------------------------------------------- #

RATES = {
    "seasonId": 3,
    "productId": 8,
    "deductibleId": 13,
    "mode": "deductible",
    "aggregateValue": "12.761325",
    "aggregateRiskValue": "9.000000",
    "aggregateExpectedYieldKgHa": None,
    "areaHa": 4.0,
    "polygons": [
        {
            "polygonIndex": 0,
            "runId": 900,
            "cellM": 10,
            "aggregateValue": "13.190000",
            "aggregateRiskValue": "10.000000",
            "areaHa": 3.0,
            "tileCount": 300,
            "layers": [LAYER],
        },
        {
            "polygonIndex": 1,
            "runId": 901,
            "cellM": 30,
            "aggregateValue": "11.475300",
            "aggregateRiskValue": "6.000000",
            "areaHa": 1.0,
            "tileCount": 12,
            "layers": [LAYER],
        },
    ],
}


async def test_the_rate_of_a_sale_is_one_request_for_every_polygon_and_names_no_grid() -> None:
    recorder = _answer(200, RATES)
    async with client_for(recorder) as gis:
        rate = await gis.underwriting.resolve_rates(
            [FIRST, SECOND], season_id=3, product_id=8, deductible_id=13
        )

    [request] = recorder.requests
    assert (request.method, request.url.path) == ("POST", "/api/v1/rates/resolve/polygons")
    # No grid is sent: the API resolves each polygon on the finest it affords.
    assert json.loads(request.content) == {
        "geometries": [FIRST, SECOND],
        "seasonId": 3,
        "productId": 8,
        "deductibleId": 13,
        "cellM": None,
    }
    # The sale, and each polygon beside the run that pins it.
    assert (rate.aggregate_value, rate.aggregate_risk_value, rate.area_ha) == (
        D("12.761325"),
        D("9.000000"),
        4.0,
    )
    assert [(item.polygon_index, item.run_id, item.cell_m) for item in rate.polygons] == [
        (0, 900, 10),
        (1, 901, 30),
    ]
    assert rate.polygons[0].layers[0].name == "Fraiburgo"


async def test_a_shapely_geometry_is_a_polygon_like_any_other() -> None:
    class Drawn:
        __geo_interface__ = FIRST

    recorder = _answer(200, RATES)
    async with client_for(recorder) as gis:
        await gis.underwriting.resolve_rates([Drawn()], season_id=3, product_id=8, deductible_id=13)

    assert json.loads(recorder.requests[0].content)["geometries"] == [FIRST]


REFUSED = {
    "type": "urn:problem-type:rates.resolve.polygons_refused",
    "title": "Unprocessable Content",
    "status": 422,
    "detail": "2 of 3 polygons cannot be resolved, so none was",
    "code": "rates.resolve.polygons_refused",
    "correlationId": "c0ffee",
    "polygon_count": 3,
    "refused_count": 2,
    "refused": [
        {
            "polygon_index": 1,
            "code": "rates.resolve.forbidden_area",
            "detail": "12 of 300 tiles lie in ground where this produto may not be sold",
            "context": {
                "forbidden_area_pct": 4.0,
                "forbidding_areas": [{"area_id": 77, "name": "Reserva"}],
            },
        },
        {
            "polygon_index": 2,
            "code": "rates.resolve.unpriced_area",
            "detail": "30 of 300 tiles have no rate at any level for this cell",
            "context": {"unresolved_area_pct": 10.0},
        },
    ],
}


async def test_a_polygon_that_cannot_be_resolved_is_one_error_naming_each_and_why() -> None:
    async with client_for(_answer(422, REFUSED)) as gis:
        with pytest.raises(sdk.PolygonsRefusedError) as raised:
            await gis.underwriting.resolve_rates(
                [FIRST, SECOND, FIRST], season_id=3, product_id=8, deductible_id=13
            )

    error = raised.value
    assert isinstance(error, sdk.UnprocessableError)
    assert (error.status, error.code, error.correlation_id) == (
        422,
        "rates.resolve.polygons_refused",
        "c0ffee",
    )
    forbidden, unpriced = error.refusals
    assert (forbidden.polygon_index, forbidden.code) == (1, sdk.RateRefusalCode.FORBIDDEN_AREA)
    assert forbidden.context["forbidding_areas"] == [{"area_id": 77, "name": "Reserva"}]
    assert (unpriced.polygon_index, unpriced.code) == (2, sdk.RateRefusalCode.UNPRICED_AREA)
    assert unpriced.detail.startswith("30 of 300 tiles")
    # The body stays whole beside the typed view of it.
    assert error.context["refused_count"] == 2


@pytest.mark.parametrize(
    "refused",
    [
        None,
        [],
        "polygon 1",
        [{"polygon_index": "1", "code": "x", "detail": "y", "context": {}}],
        [{"polygon_index": True, "code": "x", "detail": "y", "context": {}}],
        [{"polygon_index": 1, "code": "x", "detail": "y"}],
    ],
)
async def test_a_refusal_listed_in_a_shape_this_version_cannot_read_is_typed_by_its_status(
    refused: object,
) -> None:
    """Never a guess: the caller still gets the 422 and the untouched body."""
    problem = {**REFUSED, "refused": refused}
    async with client_for(_answer(422, problem)) as gis:
        with pytest.raises(sdk.UnprocessableError) as raised:
            await gis.underwriting.resolve_rates(
                [FIRST], season_id=3, product_id=8, deductible_id=13
            )

    assert not isinstance(raised.value, sdk.PolygonsRefusedError)
    assert raised.value.code == "rates.resolve.polygons_refused"
    assert raised.value.context["refused"] == refused


async def test_a_later_reason_the_api_adds_still_arrives_as_its_code() -> None:
    problem = {
        **REFUSED,
        "refused": [
            {"polygon_index": 0, "code": "rates.resolve.new_reason", "detail": "new", "context": {}}
        ],
    }
    async with client_for(_answer(422, problem)) as gis:
        with pytest.raises(sdk.PolygonsRefusedError) as raised:
            await gis.underwriting.resolve_rates(
                [FIRST], season_id=3, product_id=8, deductible_id=13
            )

    [refusal] = raised.value.refusals
    assert refusal.code == "rates.resolve.new_reason"
    assert refusal.code not in set(sdk.RateRefusalCode)


async def test_one_polygon_resolved_alone_may_name_no_grid() -> None:
    """`gis.rates.resolve`: `cell_m` is optional, and sent as given."""
    recorder = _answer(599, {"detail": "recorded", "code": "test.recorded"})
    async with client_for(recorder) as gis:
        with pytest.raises(sdk.ApiError):
            await gis.rates.resolve(FIRST, product_id=8, deductible_id=13)
        with pytest.raises(sdk.ApiError):
            await gis.rates.resolve(FIRST, product_id=8, deductible_id=13, cell_m=100)

    unnamed, named = (json.loads(request.content) for request in recorder.requests)
    assert unnamed["cellM"] is None
    assert named["cellM"] == 100


# --------------------------------------------------------------------------- #
# After the purchase: the contract is screened
# --------------------------------------------------------------------------- #

SCREENING = {
    "runId": 55,
    "generatedAt": "2026-10-13T14:30:00Z",
    "asOf": "2026-10-13T14:30:00Z",
    "results": [
        {
            "codImovel": "SC-4205506-0001",
            "outcome": "screened",
            "property": {"codImovel": "SC-4205506-0001", "status": "AT", "geometry": FIRST},
            "findings": [
                {
                    "source": "ibama",
                    "dataset": "embargos",
                    "category": "embargo",
                    "properties": {"num_tad": "123"},
                    "overlapHa": 1.5,
                    "overlapPct": 1.25,
                    "measuredAgainst": "imovel",
                    "normReference": {"article": "art. 8"},
                }
            ],
        },
        {"codImovel": "SC-0000000-9999", "outcome": "not_in_snapshot", "note": "not held"},
    ],
    "sources": [SNAPSHOT],
    "notCovered": ["trabalho escravo"],
    "disclaimer": "reports, never decides",
}


async def test_car_properties_are_screened_by_their_codes_and_nothing_else() -> None:
    recorder = _answer(200, SCREENING)
    async with client_for(recorder) as gis:
        screened = await gis.underwriting.screen_car_properties(
            ["SC-4205506-0001", "SC-0000000-9999"]
        )

    [request] = recorder.requests
    assert (request.method, request.url.path) == ("POST", "/api/v1/screening")
    # Codes only: no polygon travels with a CAR screening.
    assert json.loads(request.content) == {
        "items": [{"codImovel": "SC-4205506-0001"}, {"codImovel": "SC-0000000-9999"}]
    }
    found, missing = screened.results
    assert found.outcome is sdk.ScreeningOutcome.SCREENED
    assert found.findings[0].measured_against is sdk.FindingMeasuredAgainst.PROPERTY
    # A code the SICAR copy does not hold is its own answer, not a failure.
    assert missing.outcome is sdk.ScreeningOutcome.NOT_IN_SNAPSHOT
    assert screened.run_id == 55


POLYGON_SCREENING = {
    "polygons": [
        {
            "polygonIndex": 0,
            "car": {"total": 0, "coveredPct": 0.0, "items": []},
            "esg": [
                {
                    "source": "icmbio",
                    "dataset": "ucs",
                    "category": "unidade_conservacao",
                    "name": "APA",
                    "properties": {},
                    "overlapHa": 3.5,
                    "overlapPct": 20.0,
                    "supplementary": False,
                }
            ],
            "esgCoveredPct": 20.0,
        },
        {
            "polygonIndex": 1,
            "car": {"total": 0, "coveredPct": 0.0, "items": []},
            "esg": [],
            "esgCoveredPct": 0.0,
        },
    ],
    "sources": [SNAPSHOT],
}


async def test_the_polygons_of_a_contract_are_screened_in_one_request() -> None:
    recorder = _answer(200, POLYGON_SCREENING)
    async with client_for(recorder) as gis:
        screened = await gis.underwriting.screen_polygons([FIRST, SECOND])

    [request] = recorder.requests
    assert (request.method, request.url.path) == ("POST", "/api/v1/screening/overlaps/polygons")
    assert json.loads(request.content) == {"geometries": [FIRST, SECOND], "limit": None}
    first, second = screened.polygons
    assert (first.polygon_index, first.esg_covered_pct) == (0, 20.0)
    assert first.esg[0].category == "unidade_conservacao"
    assert (second.polygon_index, second.esg) == (1, [])
    assert [source.source_key for source in screened.sources] == ["sicar"]


POLICY_OVERLAP = {
    "checkedSeasons": [
        {"id": 3, "label": "2026/2027", "ordinal": 2, "isLatest": True, "retiredAt": None}
    ],
    "checkedPlantingWindows": [],
    "uncheckedUndatedSeasons": [],
    "totalMatches": 1,
    "polygons": [
        {
            "polygonIndex": 0,
            "totalMatches": 1,
            "matches": [
                {
                    "policyId": "AP-1",
                    "areaId": 77,
                    "seasonId": 3,
                    "seasonLabel": "2026/2027",
                    "productId": 8,
                    "productCode": "PERA",
                    "isRunning": True,
                    "overlapHa": 2.5,
                    "overlapPct": 12.5,
                    "geometry": FIRST,
                }
            ],
        },
        {"polygonIndex": 1, "totalMatches": 0, "matches": []},
    ],
}


async def test_the_policy_overlap_is_asked_once_for_every_polygon_with_its_filters() -> None:
    recorder = _answer(200, POLICY_OVERLAP)
    async with client_for(recorder) as gis:
        overlap = await gis.underwriting.check_policy_overlap(
            [FIRST, SECOND],
            product_id=8,
            season_ids=[3],
            running_only=False,
            planting_window_ids=[4, 5],
        )

    [request] = recorder.requests
    assert (request.method, request.url.path) == ("POST", "/api/v1/policies/overlap/polygons")
    assert json.loads(request.content) == {
        "geometries": [FIRST, SECOND],
        "productId": 8,
        "seasonIds": [3],
        "runningOnly": False,
        "plantingWindowIds": [4, 5],
    }
    assert overlap.total_matches == 1
    collided, clear = overlap.polygons
    assert (collided.matches[0].policy_id, collided.matches[0].overlap_pct) == ("AP-1", 12.5)
    assert (clear.polygon_index, clear.matches) == (1, [])
    assert [season.label for season in overlap.checked_seasons] == ["2026/2027"]


async def test_a_policy_overlap_with_no_filter_asks_running_policies_of_the_open_seasons() -> None:
    recorder = _answer(200, POLICY_OVERLAP)
    async with client_for(recorder) as gis:
        await gis.underwriting.check_policy_overlap([FIRST])

    assert json.loads(recorder.requests[0].content) == {
        "geometries": [FIRST],
        "productId": None,
        "seasonIds": None,
        "runningOnly": True,
        "plantingWindowIds": None,
    }


async def test_every_call_of_a_sale_is_a_single_request() -> None:
    """Twelve polygons, nine calls, nine requests: nothing loops on the wire."""
    answers = {
        "/api/v1/rates/seasons/open": OPEN_SEASONS,
        "/api/v1/rates/seasons/3/territory": TERRITORY,
        "/api/v1/rates/seasons/3/municipalities/4205506/products": ON_SALE,
        "/api/v1/screening/preflight": CAR_PROPERTIES,
        "/api/v1/groups/validate": GROUP,
        "/api/v1/rates/resolve/polygons": RATES,
        "/api/v1/screening": SCREENING,
        "/api/v1/screening/overlaps/polygons": POLYGON_SCREENING,
        "/api/v1/policies/overlap/polygons": POLICY_OVERLAP,
    }
    recorder = Recorder(lambda request: httpx.Response(200, json=answers[request.url.path]))
    polygons = [_square(-50.87 + step * 0.01, -27.03) for step in range(12)]
    async with client_for(recorder) as gis:
        [season] = await gis.underwriting.list_open_seasons()
        await gis.underwriting.list_sold_territory(season.id)
        await gis.underwriting.list_products_on_sale(season.id, 4205506)
        await gis.underwriting.list_car_properties(polygons[0])
        await gis.underwriting.validate_group(polygons, municipality_id=4205506)
        await gis.underwriting.resolve_rates(polygons, season_id=3, product_id=8, deductible_id=13)
        await gis.underwriting.screen_car_properties(["SC-4205506-0001"])
        await gis.underwriting.screen_polygons(polygons)
        await gis.underwriting.check_policy_overlap(polygons, product_id=8)

    assert [request.url.path for request in recorder.requests] == list(answers)
