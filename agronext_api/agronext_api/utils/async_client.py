import logging
from typing import Any, Literal, Optional, TypeVar

from httpx import (
    AsyncClient,
    HTTPError,  # noqa: F401
    HTTPStatusError,
    RequestError,
    Response,
    codes,
)

from ..logger import get_logger

logger = get_logger("async_client")

logger.setLevel(logging.INFO)

METHODS = Literal["GET", "POST", "PUT", "DELETE"]
T = TypeVar("T")


class ResponseError(HTTPError):
    def __init__(self, message: str, *, response: Response) -> None:
        super().__init__(message)
        self.response = response


class BaseAsyncClient(AsyncClient):
    def __init__(
        self,
        *,
        base_url: str,
        headers: Optional[dict[str, str]] = None,
        timeout: float = 15.0,
        follow_redirects: bool = True,
        max_redirects: int = 5,
        **kwargs: Any,
    ):
        super().__init__(
            base_url=base_url,
            headers=headers,
            timeout=timeout,
            follow_redirects=follow_redirects,
            max_redirects=max_redirects,
            **kwargs,
        )

    async def close(self) -> None:
        await super().aclose()

    @staticmethod
    def _handle_response(response: Response, response_model: Optional[T]) -> Response | T:
        response.raise_for_status()
        if response_model and (response.status_code in [codes.OK, codes.CREATED]):
            try:
                response_json = response.json()
                if isinstance(response_json, dict):
                    return response_model(**response_json)
                return response_model(response_json)
            except Exception:
                raise ResponseError(f"Failed to parse response to {response_model}", response)
        return response

    @staticmethod
    async def request(
        *,
        method: METHODS = "GET",
        url: str,
        payload: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        response_model: Optional[T] = None,
        **kwargs: Any,
    ) -> Response | T:
        async with AsyncClient() as client:
            response = await client.request(method, url, data=payload, headers=headers, **kwargs)
            response = BaseAsyncClient._handle_response(response, response_model)
            return response

    async def _request(
        self,
        method: METHODS,
        url: str,
        response_model: Optional[T] = None,
        **kwargs: Any,
    ) -> Response | T:
        try:
            response = await super().request(method, url, **kwargs)
            response = BaseAsyncClient._handle_response(response, response_model)
        except HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            raise
        except RequestError as e:
            logger.error(f"An error occurred while requesting {e.request.url!r}.")
            raise
        except ResponseError as e:
            logger.error(f"{e}")
            raise

        return response

    async def get(self, url: str, response_model: Optional[T] = None, **kwargs) -> Response | T:
        return await self._request("GET", url, response_model, **kwargs)

    async def post(self, url: str, response_model: Optional[T] = None, **kwargs) -> Response | T:
        return await self._request("POST", url, response_model, **kwargs)

    async def put(self, url: str, response_model: Optional[T] = None, **kwargs) -> Response | T:
        return await self._request("PUT", url, response_model, **kwargs)

    async def delete(self, url: str, response_model: Optional[T] = None, **kwargs) -> Response | T:
        return await self._request("DELETE", url, response_model, **kwargs)
