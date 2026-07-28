"""Incremental export API client."""

from typing import TYPE_CHECKING, Any, Dict, Optional

from ..pagination import ZendeskPaginator
from .base import BaseClient

if TYPE_CHECKING:
    from ..http_client import HTTPClient
    from ..pagination import Paginator


class IncrementalClient(BaseClient):
    """Client for Zendesk incremental export endpoints."""

    def ticket_events(
        self,
        start_time: int,
        *,
        limit: Optional[int] = None,
    ) -> "Paginator[Dict[str, Any]]":
        """Iterate incremental ticket events from a Unix start_time."""
        return ZendeskPaginator.create_incremental_paginator(
            self._http, "ticket_events", start_time, limit=limit
        )

    def ticket_metric_events(
        self,
        start_time: int,
        *,
        limit: Optional[int] = None,
    ) -> "Paginator[Dict[str, Any]]":
        """Iterate incremental ticket metric events from a Unix start_time."""
        return ZendeskPaginator.create_incremental_paginator(
            self._http, "ticket_metric_events", start_time, limit=limit
        )
