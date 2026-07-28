"""Custom ticket status models for Zendesk API."""

from datetime import datetime
from typing import Optional

from pydantic import Field

from .base import ZendeskModel


class CustomStatus(ZendeskModel):
    """Zendesk custom ticket status (Enterprise)."""

    id: Optional[int] = Field(default=None, description="The custom status ID")
    url: Optional[str] = Field(default=None, description="The API URL of the custom status")
    status_category: Optional[str] = Field(default=None, description="Underlying status category (new, open, pending, hold, solved)")
    agent_label: Optional[str] = Field(default=None, description="Label shown to agents")
    end_user_label: Optional[str] = Field(default=None, description="Label shown to end users")
    description: Optional[str] = Field(default=None, description="Description of the custom status")
    active: Optional[bool] = Field(default=None, description="Whether the custom status is active")
    default: Optional[bool] = Field(default=None, description="Whether this is the default for its category")
    created_at: Optional[datetime] = Field(default=None, description="When the custom status was created")
    updated_at: Optional[datetime] = Field(default=None, description="When the custom status was last updated")
