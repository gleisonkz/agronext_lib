import logging
from enum import StrEnum
from typing import Any, Optional, Type, TypeVar, TypedDict, Callable

from httpx import (
    AsyncClient,
    HTTPError,
    HTTPStatusError,
    RequestError,
    Response,
    codes,
    URL,
)

logger = logging.getLogger("async_client")

T = TypeVar("T")


class HTTPMethods(StrEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class ResponseError(HTTPError):
    def __init__(self, message: str, *, response: Response | None = None, exception: Exception | None = None,) -> None:
        super().__init__(message)
        self.response = response
        self.exception = exception


class RequestOptions(TypedDict, total=False):
    auth: Optional[Any]
    headers: Optional[Any]
    cookies: Optional[Any]
    files: Optional[Any]
    timeout: Optional[Any]
    follow_redirects: bool
    extensions: Optional[dict[str, Any]]


class InitOptions(TypedDict, total=False):
    auth: Optional[Any]
    params: Optional[Any]
    cookies: Optional[Any]
    cert: Optional[Any]
    verify: Optional[bool]
    http1: Optional[bool]
    http2: Optional[bool]
    proxy: Optional[Any]
    mounts: Optional[Any]
    limits: Optional[Any]
    event_hooks: Optional[Any]
    transport: Optional[Any]
    trust_env: Optional[bool]
    default_encoding: Optional[str | Callable[[bytes], str]]


class BaseAsyncClient(AsyncClient):
    def __init__(
        self,
        *,
        base_url: str | URL,
        headers: Optional[dict[str, str]] = None,
        follow_redirects: bool = True,
        max_redirects: int = 5,
        timeout: float = 15.0,
        options: Optional[InitOptions] = None,
    ):
        if options is None:
            options = {}

        super().__init__(
            base_url=base_url,
            headers=headers,
            timeout=timeout,
            follow_redirects=follow_redirects,
            max_redirects=max_redirects,
            **options,
        )

    @staticmethod
    def _handle_response(
        response: Response,
        response_model: Optional[Type[T]] = None,
    ) -> Response | T:
        response.raise_for_status()
        if response_model and (response.status_code in [codes.OK, codes.CREATED]):
            try:
                response_json = response.json()
                if isinstance(response_json, dict):
                    return response_model(**response_json)
                return response_model(response_json)
            except Exception as e:
                print(e)
                raise ResponseError(
                    f"Failed to parse response to {response_model}", 
                    response=response,
                    exception=e
                ) from None
        return response

    async def _request(
        self,
        method: HTTPMethods,
        *,
        endpoint: str | URL,
        payload: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        response_model: Optional[Type[T]] = None,
        options: Optional[RequestOptions] = None,
    ) -> Response | T:
        if not isinstance(method, HTTPMethods):
            raise RequestError(f"Invalid HTTP method: {method!r}")

        if options is None:
            options = {}

        try:
            response = await self.request(
                method,
                endpoint,
                json=payload,
                params=params,
                **options,
            )
            response = self._handle_response(response, response_model)
        except HTTPStatusError as e:
            logger.error(
                f"HTTP error occurred: {e.response.status_code} - {e.response.text}"
            )
            raise
        except RequestError as e:
            logger.error(f"An error occurred while requesting {e.request.url!r}.")
            raise
        except ResponseError as e:
            logger.error(f"{e}")
            raise

        return response

    async def get(
        self,
        endpoint: str | URL,
        params: Optional[dict[str, Any]] = None,
        response_model: Optional[Type[T]] = None,
        options: Optional[RequestOptions] = None,
    ) -> Response | T:
        return await self._request(
            HTTPMethods.GET,
            endpoint=endpoint,
            params=params,
            response_model=response_model,
            options=options,
        )

    async def post(
        self,
        endpoint: str | URL,
        payload: Optional[dict[str, Any]] = None,
        response_model: Optional[Type[T]] = None,
        options: Optional[RequestOptions] = None,
    ) -> Response | T:
        return await self._request(
            HTTPMethods.POST,
            endpoint=endpoint,
            payload=payload,
            response_model=response_model,
            options=options,
        )

    async def put(
        self,
        endpoint: str | URL,
        payload: Optional[dict[str, Any]] = None,
        response_model: Optional[Type[T]] = None,
        options: Optional[RequestOptions] = None,
    ) -> Response | T:
        return await self._request(
            HTTPMethods.PUT,
            endpoint=endpoint,
            payload=payload,
            response_model=response_model,
            options=options,
        )

    async def patch(
        self,
        endpoint: str | URL,
        payload: Optional[dict[str, Any]] = None,
        response_model: Optional[Type[T]] = None,
        options: Optional[RequestOptions] = None,
    ) -> Response | T:
        return await self._request(
            HTTPMethods.PATCH,
            endpoint=endpoint,
            payload=payload,
            response_model=response_model,
            options=options,
        )

    async def delete(
        self,
        endpoint: str | URL,
        payload: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        response_model: Optional[Type[T]] = None,
        options: Optional[RequestOptions] = None,
    ) -> Response | T:
        return await self._request(
            HTTPMethods.DELETE,
            endpoint=endpoint,
            payload=payload,
            params=params,
            response_model=response_model,
            options=options,
        )
