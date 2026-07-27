"""Automations API client."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from ..models.trigger import Automation
from ..pagination import ZendeskPaginator
from .base import BaseClient

if TYPE_CHECKING:
    from ..http_client import HTTPClient
    from ..pagination import Paginator


class AutomationsClient(BaseClient):
    """Client for Zendesk Automations API."""

    def list(self, per_page: int = 100, limit: Optional[int] = None) -> "Paginator[Automation]":
        """Get paginated list of automations."""
        return ZendeskPaginator.create_automations_paginator(self._http, per_page=per_page, limit=limit)

    async def get(self, automation_id: int) -> Automation:
        """Get an automation by ID."""
        response = await self._get(f"automations/{automation_id}.json")
        return Automation(**response["automation"])

    async def create(
        self,
        title: str,
        *,
        actions: List[Dict[str, Any]],
        conditions: Optional[Dict[str, Any]] = None,
        active: Optional[bool] = None,
        position: Optional[int] = None,
    ) -> Automation:
        """Create an automation."""
        automation_data: Dict[str, Any] = {"title": title, "actions": actions}
        if conditions is not None:
            automation_data["conditions"] = conditions
        if active is not None:
            automation_data["active"] = active
        if position is not None:
            automation_data["position"] = position

        response = await self._post("automations.json", json={"automation": automation_data})
        return Automation(**response["automation"])

    async def update(
        self,
        automation_id: int,
        *,
        title: Optional[str] = None,
        actions: Optional[List[Dict[str, Any]]] = None,
        conditions: Optional[Dict[str, Any]] = None,
        active: Optional[bool] = None,
        position: Optional[int] = None,
    ) -> Automation:
        """Update an automation."""
        automation_data: Dict[str, Any] = {}
        if title is not None:
            automation_data["title"] = title
        if actions is not None:
            automation_data["actions"] = actions
        if conditions is not None:
            automation_data["conditions"] = conditions
        if active is not None:
            automation_data["active"] = active
        if position is not None:
            automation_data["position"] = position

        response = await self._put(f"automations/{automation_id}.json", json={"automation": automation_data})
        return Automation(**response["automation"])

    async def delete(self, automation_id: int) -> bool:
        """Delete an automation."""
        await self._delete(f"automations/{automation_id}.json")
        return True
