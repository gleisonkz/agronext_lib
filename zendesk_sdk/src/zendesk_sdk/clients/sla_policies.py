"""SLA Policies API client."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from ..models.sla import SlaPolicy
from ..pagination import ZendeskPaginator
from .base import BaseClient

if TYPE_CHECKING:
    from ..http_client import HTTPClient
    from ..pagination import Paginator


class SlaPoliciesClient(BaseClient):
    """Client for Zendesk SLA Policies API."""

    def list(self, per_page: int = 100, limit: Optional[int] = None) -> "Paginator[SlaPolicy]":
        """Get paginated list of SLA policies."""
        return ZendeskPaginator.create_sla_policies_paginator(self._http, per_page=per_page, limit=limit)

    async def get(self, policy_id: int) -> SlaPolicy:
        """Get an SLA policy by ID."""
        response = await self._get(f"slas/policies/{policy_id}.json")
        return SlaPolicy(**response["sla_policy"])

    async def create(
        self,
        title: str,
        *,
        filter: Optional[Dict[str, Any]] = None,
        policy_metrics: Optional[List[Dict[str, Any]]] = None,
        description: Optional[str] = None,
        position: Optional[int] = None,
    ) -> SlaPolicy:
        """Create an SLA policy."""
        policy_data: Dict[str, Any] = {"title": title}
        if filter is not None:
            policy_data["filter"] = filter
        if policy_metrics is not None:
            policy_data["policy_metrics"] = policy_metrics
        if description is not None:
            policy_data["description"] = description
        if position is not None:
            policy_data["position"] = position

        response = await self._post("slas/policies.json", json={"sla_policy": policy_data})
        return SlaPolicy(**response["sla_policy"])

    async def update(
        self,
        policy_id: int,
        *,
        title: Optional[str] = None,
        filter: Optional[Dict[str, Any]] = None,
        policy_metrics: Optional[List[Dict[str, Any]]] = None,
        description: Optional[str] = None,
        position: Optional[int] = None,
    ) -> SlaPolicy:
        """Update an SLA policy."""
        policy_data: Dict[str, Any] = {}
        if title is not None:
            policy_data["title"] = title
        if filter is not None:
            policy_data["filter"] = filter
        if policy_metrics is not None:
            policy_data["policy_metrics"] = policy_metrics
        if description is not None:
            policy_data["description"] = description
        if position is not None:
            policy_data["position"] = position

        response = await self._put(f"slas/policies/{policy_id}.json", json={"sla_policy": policy_data})
        return SlaPolicy(**response["sla_policy"])
