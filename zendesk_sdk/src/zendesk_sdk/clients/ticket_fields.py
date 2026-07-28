"""Ticket Fields API client."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from ..models.ticket import TicketField
from ..pagination import ZendeskPaginator
from .base import BaseClient

if TYPE_CHECKING:
    from ..config import CacheConfig
    from ..http_client import HTTPClient
    from ..pagination import Paginator


class TicketFieldsClient(BaseClient):
    """Client for Zendesk Ticket Fields API.

    Provides access to ticket field definitions, including both system
    fields and custom fields. Essential for understanding ticket schema.

    Example:
        async with ZendeskClient(config) as client:
            # Get all ticket fields
            async for field in client.ticket_fields.list():
                print(f"{field.title}: {field.type}")

            # Get a specific field by ID
            field = await client.ticket_fields.get(12345)

            # Find field by title
            field = await client.ticket_fields.get_by_title("Subscription")
    """

    def __init__(
        self,
        http_client: "HTTPClient",
        cache_config: Optional["CacheConfig"] = None,
    ) -> None:
        """Initialize TicketFieldsClient with optional caching."""
        super().__init__(http_client, cache_config)
        # Ticket fields change infrequently, use longer TTL (30 minutes)
        if cache_config:
            maxsize = getattr(cache_config, "ticket_field_maxsize", 200)
            ttl = getattr(cache_config, "ticket_field_ttl", 1800)
        else:
            maxsize = 200
            ttl = 1800
        self.get = self._create_cached_method(self._get_impl, maxsize=maxsize, ttl=ttl)

    async def _get_impl(self, field_id: int) -> TicketField:
        """Get a specific ticket field by ID.

        Results are cached for 30 minutes by default.

        Args:
            field_id: The ticket field's ID

        Returns:
            TicketField object
        """
        response = await self._get(f"ticket_fields/{field_id}.json")
        return TicketField(**response["ticket_field"])

    def list(self, per_page: int = 100, limit: Optional[int] = None) -> "Paginator[TicketField]":
        """Get paginated list of all ticket fields.

        Returns both system fields and custom fields.

        Args:
            per_page: Number of fields per page (max 100)
            limit: Maximum number of items to return when iterating (None = no limit)

        Returns:
            Paginator for iterating through all ticket fields

        Example:
            # Iterate through all fields
            async for field in client.ticket_fields.list():
                print(f"{field.title} ({field.type})")

            # Collect to list
            fields = await client.ticket_fields.list().collect()
        """
        return ZendeskPaginator.create_ticket_fields_paginator(self._http, per_page=per_page, limit=limit)

    async def get_by_title(self, title: str) -> Optional[TicketField]:
        """Find a ticket field by its title.

        Args:
            title: The title of the ticket field (case-insensitive)

        Returns:
            TicketField if found, None otherwise
        """
        title_lower = title.lower()
        async for field in self.list():
            if field.title.lower() == title_lower:
                return field
        return None

    def _invalidate_get_cache(self) -> None:
        """Clear cached get() results after write operations."""
        cache_clear = getattr(self.get, "cache_clear", None)
        if callable(cache_clear):
            cache_clear()

    async def create(
        self,
        title: str,
        field_type: str,
        *,
        description: Optional[str] = None,
        visible_in_portal: Optional[bool] = None,
        editable_in_portal: Optional[bool] = None,
        required: Optional[bool] = None,
        custom_field_options: Optional[List[Dict[str, Any]]] = None,
    ) -> TicketField:
        """Create a ticket field."""
        field_data: Dict[str, Any] = {"title": title, "type": field_type}
        if description is not None:
            field_data["description"] = description
        if visible_in_portal is not None:
            field_data["visible_in_portal"] = visible_in_portal
        if editable_in_portal is not None:
            field_data["editable_in_portal"] = editable_in_portal
        if required is not None:
            field_data["required"] = required
        if custom_field_options is not None:
            field_data["custom_field_options"] = custom_field_options

        response = await self._post("ticket_fields.json", json={"ticket_field": field_data})
        self._invalidate_get_cache()
        return TicketField(**response["ticket_field"])

    async def update(
        self,
        field_id: int,
        *,
        title: Optional[str] = None,
        description: Optional[str] = None,
        active: Optional[bool] = None,
        required: Optional[bool] = None,
        visible_in_portal: Optional[bool] = None,
        editable_in_portal: Optional[bool] = None,
        custom_field_options: Optional[List[Dict[str, Any]]] = None,
    ) -> TicketField:
        """Update a ticket field."""
        field_data: Dict[str, Any] = {}
        if title is not None:
            field_data["title"] = title
        if description is not None:
            field_data["description"] = description
        if active is not None:
            field_data["active"] = active
        if required is not None:
            field_data["required"] = required
        if visible_in_portal is not None:
            field_data["visible_in_portal"] = visible_in_portal
        if editable_in_portal is not None:
            field_data["editable_in_portal"] = editable_in_portal
        if custom_field_options is not None:
            field_data["custom_field_options"] = custom_field_options

        response = await self._put(f"ticket_fields/{field_id}.json", json={"ticket_field": field_data})
        self._invalidate_get_cache()
        return TicketField(**response["ticket_field"])

    async def delete(self, field_id: int) -> bool:
        """Delete a ticket field."""
        await self._delete(f"ticket_fields/{field_id}.json")
        self._invalidate_get_cache()
        return True
