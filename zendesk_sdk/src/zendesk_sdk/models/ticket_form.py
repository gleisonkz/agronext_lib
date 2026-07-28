"""Ticket form models for Zendesk API."""

from datetime import datetime
from typing import List, Optional

from pydantic import Field

from .base import ZendeskModel


class TicketForm(ZendeskModel):
    """Zendesk ticket form definition."""

    id: Optional[int] = Field(default=None, description="Automatically assigned when created")
    url: Optional[str] = Field(default=None, description="The API URL of this ticket form")
    name: str = Field(..., description="Internal name of the ticket form")
    display_name: Optional[str] = Field(default=None, description="Display name shown to agents")
    active: Optional[bool] = Field(default=None, description="Whether the form is active")
    end_user_visible: Optional[bool] = Field(default=None, description="Whether end users can see the form")
    ticket_field_ids: Optional[List[int]] = Field(default=None, description="Ordered ticket field IDs on the form")
    position: Optional[int] = Field(default=None, description="Relative position among forms")
    created_at: Optional[datetime] = Field(default=None, description="When the form was created")
    updated_at: Optional[datetime] = Field(default=None, description="When the form was last updated")
    default: Optional[bool] = Field(default=None, description="Whether this is the default form")
