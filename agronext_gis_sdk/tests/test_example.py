"""`example.py`'s own edge: it renders, it refuses to run without its settings
and names the key, it makes the nine calls in order with each fed by the
answers before it, it prints the id of everything an option can name, and it
ends non-zero when it cannot go on — saying why.

What is pinned here is the SCRIPT, with the API stubbed at the HTTP boundary as
in every test of this package. Whether the SDK and a real API agree is not
something a stub can say: that is what running the script against one is for.
"""

import json
import logging
from collections.abc import AsyncGenerator, Iterator
from typing import Any

import httpx
import pytest
from typer.testing import CliRunner

import agronext_gis_sdk as sdk
import example

from .conftest import Recorder, client_for
from .test_underwriting import (
    CAR_PROPERTIES,
    FIRST,
    GROUP,
    ON_SALE,
    OPEN_SEASONS,
    POLICY_OVERLAP,
    POLYGON_SCREENING,
    RATES,
    REFUSED,
    SCREENING,
    SNAPSHOT,
    TERRITORY,
)

runner = CliRunner()

API = "/api/v1"
OPEN = f"{API}/rates/seasons/open"
MUNICIPALITY = {
    "id": 4205506,
    "name": "Fraiburgo",
    "stateId": 42,
    "stateAbbr": "SC",
    "centroid": [-50.87, -27.03],
    "boundary": FIRST,
    "areaHa": 54_700.0,
    "patchedPolygon": False,
    "snapshot": SNAPSHOT,
}


def _season(season_id: int, label: str) -> dict[str, Any]:
    return {
        "id": season_id,
        "label": label,
        "ordinal": season_id,
        "isLatest": True,
        "startsOn": "2026-07-01",
        "endsOn": "2027-06-30",
        "isOpen": True,
    }


#: A whole sale, answered: every path the run asks, in the order it asks them.
ANSWERS: dict[str, Any] = {
    OPEN: OPEN_SEASONS,
    f"{API}/rates/seasons/3/territory": TERRITORY,
    f"{API}/rates/seasons/3/municipalities/4205506/products": ON_SALE,
    f"{API}/geography/municipalities/4205506": MUNICIPALITY,
    f"{API}/screening/preflight": CAR_PROPERTIES,
    f"{API}/groups/validate": GROUP,
    f"{API}/rates/resolve/polygons": RATES,
    f"{API}/screening": SCREENING,
    f"{API}/screening/overlaps/polygons": POLYGON_SCREENING,
    f"{API}/policies/overlap/polygons": POLICY_OVERLAP,
}


@pytest.fixture(autouse=True)
def settings(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """The script's own block, set — and never a cached one from another test."""
    monkeypatch.setenv("GIS_BASE_URL", "http://gis.test")
    monkeypatch.setenv("GIS_API_KEY", "agx_test_key")
    example.gis_settings.cache_clear()
    yield
    example.gis_settings.cache_clear()


def _api(monkeypatch: pytest.MonkeyPatch, answers: dict[str, Any]) -> Recorder:
    """The script's client, on a stub answering `answers` by path: a body, or a
    (status, body) pair."""

    def answer(request: httpx.Request) -> httpx.Response:
        body = answers[request.url.path]
        status, content = body if isinstance(body, tuple) else (200, body)
        return httpx.Response(status, json=content)

    recorder = Recorder(answer)

    async def stubbed() -> AsyncGenerator[sdk.AgronextGisClient, None]:
        async with client_for(recorder) as gis:
            yield gis

    monkeypatch.setattr(example, "gis_client", stubbed)
    return recorder


def _paths(recorder: Recorder) -> list[str]:
    return [request.url.path for request in recorder.requests]


def _bodies(recorder: Recorder, path: str) -> list[dict[str, Any]]:
    return [
        json.loads(request.content) for request in recorder.requests if request.url.path == path
    ]


# --------------------------------------------------------------------------- #
# It renders, and it refuses to run on nothing
# --------------------------------------------------------------------------- #


def test_the_help_names_what_a_buyer_would_pick() -> None:
    result = runner.invoke(example.app, ["--help"])

    assert result.exit_code == 0
    assert all(
        flag in result.output
        for flag in ("--season-id", "--municipality-id", "--product-id", "--deductible-id")
    )


def test_without_its_settings_it_refuses_naming_the_keys(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.delenv("GIS_BASE_URL")
    monkeypatch.delenv("GIS_API_KEY")
    example.gis_settings.cache_clear()

    with caplog.at_level(logging.ERROR):
        result = runner.invoke(example.app, [])

    assert result.exit_code == example.EXIT_STOPPED
    assert "GIS_BASE_URL" in caplog.text
    assert "GIS_API_KEY" in caplog.text


def test_a_blank_ca_bundle_is_no_bundle(monkeypatch: pytest.MonkeyPatch) -> None:
    """`GIS_CA_BUNDLE=` is how an env file says "none"."""
    monkeypatch.setenv("GIS_CA_BUNDLE", "")
    example.gis_settings.cache_clear()

    assert example.gis_settings().ca_bundle is None


# --------------------------------------------------------------------------- #
# A whole sale
# --------------------------------------------------------------------------- #


def test_a_sale_makes_the_nine_calls_each_fed_by_the_answers_before(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Nothing is named: the safra is the one open today, the rest the first offered."""
    recorder = _api(monkeypatch, ANSWERS)

    result = runner.invoke(example.app, [])

    assert result.exit_code == 0, result.output
    assert _paths(recorder) == [
        OPEN,
        f"{API}/rates/seasons/3/territory",
        f"{API}/rates/seasons/3/municipalities/4205506/products",
        f"{API}/geography/municipalities/4205506",
        f"{API}/screening/preflight",
        f"{API}/screening/preflight",
        f"{API}/groups/validate",
        f"{API}/rates/resolve/polygons",
        f"{API}/screening",
        f"{API}/screening/overlaps/polygons",
        f"{API}/policies/overlap/polygons",
    ]
    # The safra came from the open ones; the município from the territory; the
    # produto and the franquia from what is on sale there; the CAR codes from
    # what lies under each field.
    [group] = _bodies(recorder, f"{API}/groups/validate")
    assert group["municipalityId"] == 4205506
    [rate] = _bodies(recorder, f"{API}/rates/resolve/polygons")
    assert (rate["seasonId"], rate["productId"], rate["deductibleId"]) == (3, 8, 13)
    assert len(rate["geometries"]) == 2
    [screening] = _bodies(recorder, f"{API}/screening")
    assert screening == {
        "items": [{"codImovel": "SC-4205506-0001"}, {"codImovel": "SC-4205506-0001"}]
    }
    [overlap] = _bodies(recorder, f"{API}/policies/overlap/polygons")
    assert (overlap["productId"], overlap["seasonIds"]) == (8, [3])
    assert overlap["geometries"] == rate["geometries"]
    # The result: a line per call, and the count that says every one was answered.
    for call in (
        "list_open_seasons",
        "list_sold_territory",
        "list_products_on_sale",
        "list_car_properties",
        "validate_group",
        "resolve_rates",
        "screen_car_properties",
        "screen_polygons",
        "check_policy_overlap",
    ):
        assert call in result.output
    assert "comercial 12.761325, risco 9.000000" in result.output
    assert result.output.rstrip().endswith("9 calls answered")


def test_every_id_an_option_takes_is_printed_before_anything_is_picked(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Nobody has to know an id in advance: the run shows each one it can be given."""
    _api(monkeypatch, ANSWERS)

    result = runner.invoke(example.app, [])

    assert "safra 3: 2026/2027, 2026-07-01 to 2027-06-30" in result.output
    assert "SC: 2 município(s), the first 4205506 Fraiburgo" in result.output
    assert "produto 8: PERA (Pera, Granizo); franquias 13: 0.2000, 14: 0.2500" in result.output
    assert "picked: produto 8 (PERA), franquia 13 (0.2000)" in result.output


def test_what_the_run_names_is_what_is_sold(monkeypatch: pytest.MonkeyPatch) -> None:
    recorder = _api(monkeypatch, ANSWERS)

    named = ["--season-id", "3", "--municipality-id", "4205506"]
    result = runner.invoke(example.app, [*named, "--product-id", "8", "--deductible-id", "14"])

    assert result.exit_code == 0, result.output
    # The open safras are still asked first: a sale starts there.
    assert _paths(recorder)[0] == OPEN
    [rate] = _bodies(recorder, f"{API}/rates/resolve/polygons")
    assert (rate["seasonId"], rate["productId"], rate["deductibleId"]) == (3, 8, 14)
    assert "picked: produto 8 (PERA), franquia 14 (0.2500)" in result.output


def test_a_safra_named_that_is_not_open_is_walked_and_said_not_to_be_a_sale(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """The API answers for any safra, so the run does too — but it says so."""
    closed = {
        key.replace("/seasons/3/", "/seasons/1/"): value
        for key, value in ANSWERS.items()
        if key != OPEN
    }
    _api(monkeypatch, {OPEN: OPEN_SEASONS, **closed})

    with caplog.at_level(logging.WARNING):
        result = runner.invoke(example.app, ["--season-id", "1"])

    assert result.exit_code == 0, result.output
    assert "safra 1 is not open today" in caplog.text
    assert "safra 3: 2026/2027" in result.output


def test_a_safra_named_among_the_open_ones_is_not_remarked_on(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    _api(monkeypatch, ANSWERS)

    with caplog.at_level(logging.WARNING):
        result = runner.invoke(example.app, ["--season-id", "3"])

    assert result.exit_code == 0, result.output
    assert "is not open today" not in caplog.text


# --------------------------------------------------------------------------- #
# It cannot go on: exit 2, saying why
# --------------------------------------------------------------------------- #


def test_no_safra_open_today_stops_the_run(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    recorder = _api(monkeypatch, {OPEN: []})

    with caplog.at_level(logging.ERROR):
        result = runner.invoke(example.app, [])

    assert result.exit_code == example.EXIT_STOPPED
    assert "no safra is open today" in result.output
    assert "no safra is open today, so nothing is being sold" in caplog.text
    assert _paths(recorder) == [OPEN]


def test_several_safras_open_and_none_named_stops_the_run_showing_their_ids(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    recorder = _api(monkeypatch, {OPEN: [_season(4, "2027/2028"), _season(3, "2026/2027")]})

    with caplog.at_level(logging.ERROR):
        result = runner.invoke(example.app, [])

    assert result.exit_code == example.EXIT_STOPPED
    # The ids to choose from are on the screen before the stop.
    assert "safra 4: 2027/2028" in result.output
    assert "safra 3: 2026/2027" in result.output
    assert "2 safras are open today: name the one being sold with --season-id" in caplog.text
    assert _paths(recorder) == [OPEN]


def test_a_safra_with_nothing_on_sale_stops_the_run(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    nothing: dict[str, Any] = {"seasonId": 3, "refreshedAt": None, "states": []}
    recorder = _api(monkeypatch, {OPEN: OPEN_SEASONS, f"{API}/rates/seasons/3/territory": nothing})

    with caplog.at_level(logging.ERROR):
        result = runner.invoke(example.app, [])

    assert result.exit_code == example.EXIT_STOPPED
    assert "nothing is on sale in safra 3" in caplog.text
    assert _paths(recorder) == [OPEN, f"{API}/rates/seasons/3/territory"]
    assert "calls answered" not in result.output


def test_a_produto_not_on_sale_there_stops_the_run_after_showing_what_is(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    _api(monkeypatch, ANSWERS)

    with caplog.at_level(logging.ERROR):
        result = runner.invoke(example.app, ["--product-id", "99"])

    assert result.exit_code == example.EXIT_STOPPED
    assert "produto 99 is not on sale in município 4205506 in safra 3" in caplog.text
    assert "produto 8: PERA" in result.output


def test_a_franquia_not_on_offer_stops_the_run(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    _api(monkeypatch, ANSWERS)

    with caplog.at_level(logging.ERROR):
        result = runner.invoke(example.app, ["--deductible-id", "99"])

    assert result.exit_code == example.EXIT_STOPPED
    assert "franquia 99 is not on offer for produto PERA there" in caplog.text


def test_fields_under_no_car_property_stop_the_run(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    none_there = {**CAR_PROPERTIES, "total": 0, "candidates": []}
    recorder = _api(monkeypatch, {**ANSWERS, f"{API}/screening/preflight": none_there})

    with caplog.at_level(logging.ERROR):
        result = runner.invoke(example.app, [])

    assert result.exit_code == example.EXIT_STOPPED
    assert "no CAR imóvel lies under the fields" in caplog.text
    assert f"{API}/rates/resolve/polygons" not in _paths(recorder)


def test_fields_that_cannot_be_sold_stop_the_run_naming_each_and_why(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    recorder = _api(monkeypatch, {**ANSWERS, f"{API}/rates/resolve/polygons": (422, REFUSED)})

    with caplog.at_level(logging.ERROR):
        result = runner.invoke(example.app, [])

    assert result.exit_code == example.EXIT_STOPPED
    assert "polygon 1: rates.resolve.forbidden_area" in caplog.text
    assert "polygon 2: rates.resolve.unpriced_area" in caplog.text
    # No purchase, so nothing goes to underwriting.
    assert _paths(recorder)[-1] == f"{API}/rates/resolve/polygons"


# --------------------------------------------------------------------------- #
# A request failed: exit 1, naming the request
# --------------------------------------------------------------------------- #


def test_a_request_the_api_refuses_fails_the_run_naming_it(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    problem = {
        "status": 404,
        "detail": "season 9 does not exist",
        "code": "resource.not_found",
        "correlationId": "c0ffee",
    }
    _api(monkeypatch, {OPEN: OPEN_SEASONS, f"{API}/rates/seasons/9/territory": (404, problem)})

    with caplog.at_level(logging.ERROR):
        result = runner.invoke(example.app, ["--season-id", "9"])

    assert result.exit_code == example.EXIT_FAILED
    assert "GET http://gis.test/api/v1/rates/seasons/9/territory" in caplog.text
    assert "404 resource.not_found: season 9 does not exist" in caplog.text
    assert "correlation id c0ffee" in caplog.text


def test_an_answer_the_sdk_cannot_read_fails_the_run_saying_what_did_not_fit(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """What a validation run exists to find: the API and the SDK disagreeing."""
    drifted = {"seasonId": 3, "refreshedAt": None, "states": [{"stateId": 42}]}
    _api(monkeypatch, {OPEN: OPEN_SEASONS, f"{API}/rates/seasons/3/territory": drifted})

    with caplog.at_level(logging.ERROR):
        result = runner.invoke(example.app, [])

    assert result.exit_code == example.EXIT_FAILED
    assert "the answer does not fit" in caplog.text
    # The field the answer was missing, from the cause.
    assert "abbr" in caplog.text
