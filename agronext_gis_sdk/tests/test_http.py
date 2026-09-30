"""How the client speaks HTTP: credentials, correlation, errors, encoding."""

import datetime
import decimal
import json
from typing import Any

import httpx
import pytest

import agronext_gis_sdk as sdk

from .conftest import API_KEY, Recorder, client_for

D = decimal.Decimal
POINT: dict[str, Any] = {"type": "Point", "coordinates": [-47.9, -15.8]}

ME = {"id": 2, "username": "admin", "displayName": None, "canWrite": True, "isAdmin": True}


def _answer(status: int, body: object) -> Recorder:
    return Recorder(lambda request: httpx.Response(status, json=body))


def _problem(status: int, code: str, **extra: object) -> dict[str, object]:
    return {
        "type": f"urn:problem-type:{code}",
        "title": "x",
        "status": status,
        "detail": "what went wrong",
        "code": code,
        "correlationId": "c0ffee",
        **extra,
    }


# --------------------------------------------------------------------------- #
# Credentials and correlation
# --------------------------------------------------------------------------- #


async def test_every_request_carries_the_key() -> None:
    recorder = _answer(200, ME)
    async with client_for(recorder) as gis:
        me = await gis.access.me()
    assert me == sdk.CurrentUserResponse(
        id=2, username="admin", display_name=None, can_write=True, is_admin=True
    )
    [request] = recorder.requests
    assert request.headers["X-API-Key"] == API_KEY
    assert request.url.path == "/api/v1/access/me"


async def test_the_callers_request_id_travels_when_it_has_one() -> None:
    recorder = _answer(200, ME)
    ids = iter(["req-1", None])
    async with client_for(recorder, request_id=lambda: next(ids)) as gis:
        await gis.access.me()
        await gis.access.me()
    assert recorder.requests[0].headers["X-Request-ID"] == "req-1"
    assert "X-Request-ID" not in recorder.requests[1].headers


async def test_a_deployment_that_renamed_the_correlation_header_is_honoured() -> None:
    recorder = _answer(200, ME)
    async with client_for(
        recorder, request_id=lambda: "req-2", request_id_header="X-Correlation-ID"
    ) as gis:
        await gis.access.me()
    assert recorder.requests[0].headers["X-Correlation-ID"] == "req-2"
    assert "X-Request-ID" not in recorder.requests[0].headers


# --------------------------------------------------------------------------- #
# Errors: typed, carrying the API's code, correlation id and context
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    ("status", "error_type"),
    [
        (401, sdk.UnauthorizedError),
        (403, sdk.ForbiddenError),
        (404, sdk.NotFoundError),
        (409, sdk.ConflictError),
        (422, sdk.UnprocessableError),
        (500, sdk.ServerError),
        (503, sdk.ServerError),
        (418, sdk.ApiError),
    ],
)
async def test_each_status_raises_its_own_error(
    status: int, error_type: type[sdk.ApiError]
) -> None:
    async with client_for(_answer(status, _problem(status, "some.code"))) as gis:
        with pytest.raises(error_type) as raised:
            await gis.access.me()
    assert type(raised.value) is error_type
    assert raised.value.status == status


async def test_a_rule_rejection_carries_its_code_correlation_and_context() -> None:
    body = _problem(422, "rates.copy.windows_undeclared", undeclared_product_ids=[8])
    async with client_for(_answer(422, body)) as gis:
        with pytest.raises(sdk.UnprocessableError) as raised:
            await gis.seasons.set_season_products(1, sdk.SeasonProductsRequest(product_ids=[8]))
    error = raised.value
    assert error.code == "rates.copy.windows_undeclared"
    assert error.correlation_id == "c0ffee"
    assert error.detail == "what went wrong"
    assert error.context == {"undeclared_product_ids": [8]}


async def test_a_validation_failure_carries_the_field_errors() -> None:
    errors = [{"loc": ["body", "label"], "msg": "Field required", "type": "missing"}]
    body = _problem(422, "request.invalid", errors=errors)
    async with client_for(_answer(422, body)) as gis:
        with pytest.raises(sdk.UnprocessableError) as raised:
            await gis.access.me()
    assert raised.value.errors == errors
    assert raised.value.context == {}


async def test_an_error_body_that_is_not_json_still_raises_typed() -> None:
    recorder = Recorder(lambda request: httpx.Response(502, text="<html>bad gateway</html>"))
    async with client_for(recorder) as gis:
        with pytest.raises(sdk.ServerError) as raised:
            await gis.access.me()
    assert raised.value.code is None
    assert raised.value.detail == "Bad Gateway"


async def test_an_error_body_claiming_json_that_does_not_parse_is_a_mismatch() -> None:
    recorder = Recorder(
        lambda request: httpx.Response(
            500, content=b"{not json", headers={"content-type": "application/problem+json"}
        )
    )
    async with client_for(recorder) as gis:
        with pytest.raises(sdk.ResponseMismatchError) as raised:
            await gis.access.me()
    assert raised.value.status == 500


async def test_a_timeout_is_a_transport_error_with_its_cause() -> None:
    def time_out(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("slow", request=request)

    async with client_for(time_out) as gis:
        with pytest.raises(sdk.TransportError) as raised:
            await gis.access.me()
    assert isinstance(raised.value.__cause__, httpx.ReadTimeout)


async def test_an_unreachable_api_is_a_transport_error() -> None:
    def refuse(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refused", request=request)

    async with client_for(refuse) as gis:
        with pytest.raises(sdk.TransportError):
            await gis.access.me()


async def test_an_answer_that_does_not_fit_is_a_mismatch_not_a_pydantic_error() -> None:
    async with client_for(_answer(200, {"id": "not a number"})) as gis:
        with pytest.raises(sdk.ResponseMismatchError) as raised:
            await gis.access.me()
    assert raised.value.status == 200


async def test_a_field_the_api_added_later_is_ignored() -> None:
    async with client_for(_answer(200, {**ME, "addedInAFutureVersion": 1})) as gis:
        assert (await gis.access.me()).username == "admin"


# --------------------------------------------------------------------------- #
# Encoding
# --------------------------------------------------------------------------- #


async def test_the_query_string_drops_none_and_repeats_lists() -> None:
    recorder = _answer(200, {"items": [], "page": 1, "size": 5, "total": 0, "pages": 0})
    async with client_for(recorder) as gis:
        await gis.areas.list_areas(
            levels=[sdk.LayerLevel.STATE, sdk.LayerLevel.MUNICIPALITY],
            include_retired=True,
            ids=[1, 2],
            size=5,
        )
    params = recorder.requests[0].url.params
    assert params.get_list("levels") == ["state", "municipality"]
    assert params.get_list("ids") == ["1", "2"]
    assert params["includeRetired"] == "true"
    assert "stateId" not in params
    assert params["page"] == "1"


async def test_a_body_is_camel_case_decimals_as_text_and_only_what_was_set() -> None:
    recorder = _answer(
        201, {"batchId": 1, "writtenAt": "2026-09-26T10:00:00Z", "operationCount": 1, "results": []}
    )
    async with client_for(recorder) as gis:
        await gis.rates.write(
            sdk.RateWriteBatchRequest(
                operations=[
                    sdk.RateWriteOperationRequest(
                        season_id=1,
                        product_id=8,
                        deductible_id=None,
                        area_id=3,
                        value=D("19.84"),
                        risk_value=D("4.96"),
                    )
                ]
            )
        )
    body = json.loads(recorder.requests[0].content)
    # `note` was never set, so the API's own default applies; `deductibleId`
    # was set to None on purpose, so it travels as null — the reference layer.
    assert body == {
        "operations": [
            {
                "seasonId": 1,
                "productId": 8,
                "deductibleId": None,
                "areaId": 3,
                "value": "19.84",
                "riskValue": "4.96",
            }
        ]
    }


async def test_answers_carry_exact_decimals_and_dates() -> None:
    item = {"id": 2, "productId": 8, "value": "0.2000", "retiredAt": None}
    async with client_for(_answer(200, [item])) as gis:
        [franquia] = await gis.products.list_deductibles(8)
    assert franquia.value == D("0.2000")

    season = {
        "id": 1,
        "label": "2026/2027",
        "ordinal": 1,
        "isLatest": True,
        "startsOn": "2026-07-01",
        "endsOn": "2027-06-30",
    }
    async with client_for(_answer(200, season)) as gis:
        latest = await gis.seasons.latest_season()
    assert latest.starts_on == datetime.date(2026, 7, 1)


async def test_a_geometry_may_be_anything_with_a_geo_interface() -> None:
    class Shape:
        __geo_interface__ = POINT

    recorder = _answer(
        200,
        {
            "country": {"id": 1, "abbr": "BR", "name": "Brasil"},
            "state": None,
            "municipality": None,
            "municipalities": [],
            "levelResolved": "country",
        },
    )
    async with client_for(recorder) as gis:
        located = await gis.geography.locate(Shape())
    assert json.loads(recorder.requests[0].content) == {"geometry": POINT}
    assert located.level_resolved is sdk.LayerLevel.COUNTRY


async def test_a_kml_upload_is_multipart_under_the_field_the_api_reads() -> None:
    summary = {
        "geometry": POINT,
        "areaHa": 1.0,
        "areaKm2": 0.01,
        "centroid": [-47.9, -15.8],
        "bbox": [-48.0, -16.0, -47.0, -15.0],
    }
    recorder = _answer(200, summary)
    async with client_for(recorder) as gis:
        measured = await gis.tools.import_kml_polygon(b"<kml/>", filename="talhao.kml")
    request = recorder.requests[0]
    assert request.headers["content-type"].startswith("multipart/form-data")
    assert b'name="file"; filename="talhao.kml"' in request.content
    assert measured.centroid == (-47.9, -15.8)


async def test_the_kml_export_answers_with_the_files_bytes() -> None:
    recorder = Recorder(lambda request: httpx.Response(200, content=b"<kml>ok</kml>"))
    async with client_for(recorder) as gis:
        document = await gis.tools.export_kml(
            sdk.KmlExportRequest(polygons=[sdk.NamedPolygonRequest(geometry=POINT)])
        )
    assert document == b"<kml>ok</kml>"


async def test_a_delete_answers_nothing() -> None:
    recorder = Recorder(lambda request: httpx.Response(204))
    async with client_for(recorder) as gis:
        await gis.policies.delete_policy_area(6)
    assert recorder.requests[0].method == "DELETE"


# --------------------------------------------------------------------------- #
# Paging
# --------------------------------------------------------------------------- #


async def test_paginate_walks_every_page() -> None:
    def page(request: httpx.Request) -> httpx.Response:
        number = int(request.url.params["page"])
        items = [{"id": number, "name": f"R{number}", "areaLevel": "state", "areaCount": 1}]
        return httpx.Response(
            200, json={"items": items, "page": number, "size": 1, "total": 3, "pages": 3}
        )

    recorder = Recorder(page)
    async with client_for(recorder) as gis:
        names = [
            region.name
            async for region in sdk.paginate(gis.regions.list_regions, include_retired=True)
        ]
    assert names == ["R1", "R2", "R3"]
    assert all(r.url.params["includeRetired"] == "true" for r in recorder.requests)
