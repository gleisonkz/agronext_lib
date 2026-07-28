"""Ticket Forms API client."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from ..models.ticket_form import TicketForm
from ..pagination import ZendeskPaginator
from .base import BaseClient

if TYPE_CHECKING:
    from ..http_client import HTTPClient
    from ..pagination import Paginator


class TicketFormsClient(BaseClient):
    """Client for Zendesk Ticket Forms API."""

    def list(self, per_page: int = 100, limit: Optional[int] = None) -> "Paginator[TicketForm]":
        """Get paginated list of ticket forms."""
        return ZendeskPaginator.create_ticket_forms_paginator(self._http, per_page=per_page, limit=limit)

    async def get(self, form_id: int) -> TicketForm:
        """Get a ticket form by ID."""
        response = await self._get(f"ticket_forms/{form_id}.json")
        return TicketForm(**response["ticket_form"])

    async def create(
        self,
        name: str,
        *,
        display_name: Optional[str] = None,
        active: Optional[bool] = None,
        end_user_visible: Optional[bool] = None,
        ticket_field_ids: Optional[List[int]] = None,
    ) -> TicketForm:
        """Create a ticket form."""
        form_data: Dict[str, Any] = {"name": name}
        if display_name is not None:
            form_data["display_name"] = display_name
        if active is not None:
            form_data["active"] = active
        if end_user_visible is not None:
            form_data["end_user_visible"] = end_user_visible
        if ticket_field_ids is not None:
            form_data["ticket_field_ids"] = ticket_field_ids

        response = await self._post("ticket_forms.json", json={"ticket_form": form_data})
        return TicketForm(**response["ticket_form"])

    async def update(
        self,
        form_id: int,
        *,
        name: Optional[str] = None,
        display_name: Optional[str] = None,
        active: Optional[bool] = None,
        end_user_visible: Optional[bool] = None,
        ticket_field_ids: Optional[List[int]] = None,
    ) -> TicketForm:
        """Update a ticket form."""
        form_data: Dict[str, Any] = {}
        if name is not None:
            form_data["name"] = name
        if display_name is not None:
            form_data["display_name"] = display_name
        if active is not None:
            form_data["active"] = active
        if end_user_visible is not None:
            form_data["end_user_visible"] = end_user_visible
        if ticket_field_ids is not None:
            form_data["ticket_field_ids"] = ticket_field_ids

        response = await self._put(f"ticket_forms/{form_id}.json", json={"ticket_form": form_data})
        return TicketForm(**response["ticket_form"])
