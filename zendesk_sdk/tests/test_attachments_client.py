"""Tests for the Attachments API client."""

from unittest.mock import AsyncMock, Mock, patch

import httpx

from zendesk_sdk.clients.attachments import AttachmentsClient
from zendesk_sdk.config import ZendeskConfig


def _mock_async_client_cls():
    """Wire a mock httpx.AsyncClient class as an async context manager.

    Returns (mock_cls, mock_http, response):
      - mock_cls: stand-in for httpx.AsyncClient; mock_cls.call_args captures the
        constructor kwargs (i.e. how `auth` was passed).
      - mock_http: the object yielded by `async with`; mock_http.post.call_args
        captures the request kwargs (i.e. the `headers`).
    """
    response = Mock()
    response.raise_for_status = Mock()
    response.json.return_value = {"upload": {"token": "tok123"}}

    mock_http = Mock()
    mock_http.post = AsyncMock(return_value=response)

    mock_cls = Mock()
    instance = mock_cls.return_value
    instance.__aenter__ = AsyncMock(return_value=mock_http)
    instance.__aexit__ = AsyncMock(return_value=False)
    return mock_cls, mock_http, response


class TestAttachmentsUploadAuth:
    """upload() must authenticate in both token and OAuth modes."""

    async def test_upload_oauth_mode_sends_bearer_header(self):
        """In OAuth mode upload() sends a Bearer header and passes no BasicAuth."""
        config = ZendeskConfig(subdomain="test", oauth_token="oauth_abc123")
        client = AttachmentsClient(http_client=Mock(), config=config)
        mock_cls, mock_http, _ = _mock_async_client_cls()

        with patch("zendesk_sdk.clients.attachments.httpx.AsyncClient", mock_cls):
            token = await client.upload(b"data", "file.png", "image/png")

        assert token == "tok123"
        assert mock_cls.call_args.kwargs.get("auth") is None
        assert mock_http.post.call_args.kwargs["headers"]["Authorization"] == "Bearer oauth_abc123"

    async def test_upload_token_mode_uses_basic_auth(self):
        """In token mode upload() passes BasicAuth and sends no Authorization header."""
        config = ZendeskConfig(subdomain="test", email="a@b.com", token="abc123")
        client = AttachmentsClient(http_client=Mock(), config=config)
        mock_cls, mock_http, _ = _mock_async_client_cls()

        with patch("zendesk_sdk.clients.attachments.httpx.AsyncClient", mock_cls):
            token = await client.upload(b"data", "file.png", "image/png")

        assert token == "tok123"
        assert isinstance(mock_cls.call_args.kwargs.get("auth"), httpx.BasicAuth)
        assert "Authorization" not in mock_http.post.call_args.kwargs["headers"]
