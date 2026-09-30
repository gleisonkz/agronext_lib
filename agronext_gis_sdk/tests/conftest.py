"""Test doubles at the HTTP boundary (§9.5): httpx's own MockTransport, no patching."""

from collections.abc import Callable

import httpx

from agronext_gis_sdk import AgronextGisClient

BASE_URL = "http://gis.test"
API_KEY = "agx_test_key"

type Handler = Callable[[httpx.Request], httpx.Response]


class Recorder:
    """Answers every request with `handler` and keeps each request it saw."""

    def __init__(self, handler: Handler) -> None:
        self.handler = handler
        self.requests: list[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        return self.handler(request)


def client_for(handler: Handler, **settings: object) -> AgronextGisClient:
    """A client whose network is `handler`."""
    return AgronextGisClient(
        base_url=BASE_URL,
        api_key=API_KEY,
        transport=httpx.MockTransport(handler),
        **settings,  # type: ignore[arg-type]  # each test passes the one setting it varies
    )
