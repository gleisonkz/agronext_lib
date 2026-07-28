"""Ticket audit models for Zendesk API."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from .base import ZendeskModel


class AuditEvent(ZendeskModel):
    """Single event within a ticket audit."""

    id: Optional[int] = Field(default=None, description="The event ID")
    type: Optional[str] = Field(default=None, description="Event type (e.g. Change, Comment)")
    field_name: Optional[str] = Field(default=None, description="Changed field name for Change events")
    previous_value: Optional[Any] = Field(default=None, description="Previous value before the change")
    value: Optional[Any] = Field(default=None, description="New value after the change")
    body: Optional[str] = Field(default=None, description="Comment body for Comment events")
    public: Optional[bool] = Field(default=None, description="Whether a comment event is public")
    author_id: Optional[int] = Field(default=None, description="Author of the event when applicable")
    attachments: Optional[List[Dict[str, Any]]] = Field(default=None, description="Attachments on comment events")


class Audit(ZendeskModel):
    """Ticket audit record with nested events."""

    id: Optional[int] = Field(default=None, description="The audit ID")
    ticket_id: Optional[int] = Field(default=None, description="The ticket ID")
    created_at: Optional[datetime] = Field(default=None, description="When the audit was created")
    author_id: Optional[int] = Field(default=None, description="The user who caused the audit")
    events: Optional[List[AuditEvent]] = Field(default=None, description="Events in this audit")
    via: Optional[Dict[str, Any]] = Field(default=None, description="Channel metadata for the audit")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional audit metadata")
