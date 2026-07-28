"""Triggers API client."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from ..models.trigger import Trigger
from ..pagination import ZendeskPaginator
from .base import BaseClient

if TYPE_CHECKING:
    from ..http_client import HTTPClient
    from ..pagination import Paginator


class TriggersClient(BaseClient):
    """Client for Zendesk Triggers API."""

    def list(self, per_page: int = 100, limit: Optional[int] = None) -> "Paginator[Trigger]":
        """Get paginated list of triggers."""
        return ZendeskPaginator.create_triggers_paginator(self._http, per_page=per_page, limit=limit)

    async def get(self, trigger_id: int) -> Trigger:
        """Get a trigger by ID."""
        response = await self._get(f"triggers/{trigger_id}.json")
        return Trigger(**response["trigger"])

    async def create(
        self,
        title: str,
        *,
        actions: List[Dict[str, Any]],
        conditions: Optional[Dict[str, Any]] = None,
        active: Optional[bool] = None,
        position: Optional[int] = None,
        category_id: Optional[int] = None,
    ) -> Trigger:
        """Create a trigger."""
        trigger_data: Dict[str, Any] = {"title": title, "actions": actions}
        if conditions is not None:
            trigger_data["conditions"] = conditions
        if active is not None:
            trigger_data["active"] = active
        if position is not None:
            trigger_data["position"] = position
        if category_id is not None:
            trigger_data["category_id"] = category_id

        response = await self._post("triggers.json", json={"trigger": trigger_data})
        return Trigger(**response["trigger"])

    async def update(
        self,
        trigger_id: int,
        *,
        title: Optional[str] = None,
        actions: Optional[List[Dict[str, Any]]] = None,
        conditions: Optional[Dict[str, Any]] = None,
        active: Optional[bool] = None,
        position: Optional[int] = None,
        category_id: Optional[int] = None,
    ) -> Trigger:
        """Update a trigger."""
        trigger_data: Dict[str, Any] = {}
        if title is not None:
            trigger_data["title"] = title
        if actions is not None:
            trigger_data["actions"] = actions
        if conditions is not None:
            trigger_data["conditions"] = conditions
        if active is not None:
            trigger_data["active"] = active
        if position is not None:
            trigger_data["position"] = position
        if category_id is not None:
            trigger_data["category_id"] = category_id

        response = await self._put(f"triggers/{trigger_id}.json", json={"trigger": trigger_data})
        return Trigger(**response["trigger"])

    async def delete(self, trigger_id: int) -> bool:
        """Delete a trigger."""
        await self._delete(f"triggers/{trigger_id}.json")
        return True
