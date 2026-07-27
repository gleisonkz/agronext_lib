"""Brands API client."""

from typing import TYPE_CHECKING, Optional

from ..models.brand import Brand
from ..pagination import ZendeskPaginator
from .base import BaseClient

if TYPE_CHECKING:
    from ..http_client import HTTPClient
    from ..pagination import Paginator


class BrandsClient(BaseClient):
    """Client for Zendesk Brands API (multi-brand / isolation)."""

    def list(self, per_page: int = 100, limit: Optional[int] = None) -> "Paginator[Brand]":
        """List brands (``GET /api/v2/brands``)."""
        return ZendeskPaginator.create_brands_paginator(self._http, per_page=per_page, limit=limit)

    async def get(self, brand_id: int) -> Brand:
        """Get a brand by ID."""
        response = await self._get(f"brands/{brand_id}.json")
        return Brand(**response["brand"])
