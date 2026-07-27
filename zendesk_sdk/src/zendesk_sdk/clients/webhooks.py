"""Webhooks API client.

Zendesk Webhooks API paths omit the traditional ``.json`` suffix and use
cursor pagination (``page[size]`` / ``page[after]``). See:
https://developer.zendesk.com/api-reference/webhooks/webhooks-api/webhooks/
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from ..models.webhook import Webhook
from ..pagination import ZendeskPaginator
from .base import BaseClient

if TYPE_CHECKING:
    from ..http_client import HTTPClient
    from ..pagination import Paginator


class WebhooksClient(BaseClient):
    """Client for Zendesk Webhooks API."""

    def list(self, per_page: int = 100, limit: Optional[int] = None) -> "Paginator[Webhook]":
        """Get paginated list of webhooks (``GET /api/v2/webhooks``)."""
        return ZendeskPaginator.create_webhooks_paginator(self._http, per_page=per_page, limit=limit)

    async def get(self, webhook_id: str) -> Webhook:
        """Get a webhook by ID."""
        response = await self._get(f"webhooks/{webhook_id}")
        return Webhook(**response["webhook"])

    async def create(
        self,
        name: str,
        *,
        endpoint: str,
        http_method: str = "POST",
        subscriptions: Optional[List[str]] = None,
        request_format: Optional[str] = None,
        status: Optional[str] = None,
        authentication: Optional[Dict[str, Any]] = None,
    ) -> Webhook:
        """Create a webhook."""
        webhook_data: Dict[str, Any] = {
            "name": name,
            "endpoint": endpoint,
            "http_method": http_method,
        }
        if subscriptions is not None:
            webhook_data["subscriptions"] = subscriptions
        if request_format is not None:
            webhook_data["request_format"] = request_format
        if status is not None:
            webhook_data["status"] = status
        if authentication is not None:
            webhook_data["authentication"] = authentication

        response = await self._post("webhooks", json={"webhook": webhook_data})
        return Webhook(**response["webhook"])

    async def update(
        self,
        webhook_id: str,
        *,
        name: Optional[str] = None,
        endpoint: Optional[str] = None,
        http_method: Optional[str] = None,
        subscriptions: Optional[List[str]] = None,
        status: Optional[str] = None,
        authentication: Optional[Dict[str, Any]] = None,
    ) -> Webhook:
        """Update a webhook."""
        webhook_data: Dict[str, Any] = {}
        if name is not None:
            webhook_data["name"] = name
        if endpoint is not None:
            webhook_data["endpoint"] = endpoint
        if http_method is not None:
            webhook_data["http_method"] = http_method
        if subscriptions is not None:
            webhook_data["subscriptions"] = subscriptions
        if status is not None:
            webhook_data["status"] = status
        if authentication is not None:
            webhook_data["authentication"] = authentication

        response = await self._put(f"webhooks/{webhook_id}", json={"webhook": webhook_data})
        return Webhook(**response["webhook"])

    async def delete(self, webhook_id: str) -> bool:
        """Delete a webhook."""
        await self._delete(f"webhooks/{webhook_id}")
        return True
