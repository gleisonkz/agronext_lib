"""Custom Statuses API client."""

from typing import TYPE_CHECKING, Any, Dict, Optional

from ..models.custom_status import CustomStatus
from ..pagination import ZendeskPaginator
from .base import BaseClient

if TYPE_CHECKING:
    from ..http_client import HTTPClient
    from ..pagination import Paginator


class CustomStatusesClient(BaseClient):
    """Client for Zendesk Custom Ticket Statuses API (Enterprise)."""

    def list(self, per_page: int = 100, limit: Optional[int] = None) -> "Paginator[CustomStatus]":
        """Get paginated list of custom statuses."""
        return ZendeskPaginator.create_custom_statuses_paginator(self._http, per_page=per_page, limit=limit)

    async def get(self, status_id: int) -> CustomStatus:
        """Get a custom status by ID."""
        response = await self._get(f"custom_statuses/{status_id}.json")
        return CustomStatus(**response["custom_status"])

    async def create(
        self,
        *,
        status_category: str,
        agent_label: str,
        end_user_label: Optional[str] = None,
        description: Optional[str] = None,
        active: Optional[bool] = None,
    ) -> CustomStatus:
        """Create a custom status."""
        status_data: Dict[str, Any] = {
            "status_category": status_category,
            "agent_label": agent_label,
        }
        if end_user_label is not None:
            status_data["end_user_label"] = end_user_label
        if description is not None:
            status_data["description"] = description
        if active is not None:
            status_data["active"] = active

        response = await self._post("custom_statuses.json", json={"custom_status": status_data})
        return CustomStatus(**response["custom_status"])

    async def update(
        self,
        status_id: int,
        *,
        agent_label: Optional[str] = None,
        end_user_label: Optional[str] = None,
        description: Optional[str] = None,
        active: Optional[bool] = None,
    ) -> CustomStatus:
        """Update a custom status."""
        status_data: Dict[str, Any] = {}
        if agent_label is not None:
            status_data["agent_label"] = agent_label
        if end_user_label is not None:
            status_data["end_user_label"] = end_user_label
        if description is not None:
            status_data["description"] = description
        if active is not None:
            status_data["active"] = active

        response = await self._put(f"custom_statuses/{status_id}.json", json={"custom_status": status_data})
        return CustomStatus(**response["custom_status"])
