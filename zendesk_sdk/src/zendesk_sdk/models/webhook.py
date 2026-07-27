"""Webhook models for Zendesk API."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from .base import ZendeskModel


class Webhook(ZendeskModel):
    """Zendesk webhook subscription."""

    id: Optional[str] = Field(default=None, description="The webhook ID")
    url: Optional[str] = Field(default=None, description="The API URL of the webhook")
    name: Optional[str] = Field(default=None, description="Webhook name")
    endpoint: Optional[str] = Field(default=None, description="Destination URL")
    http_method: Optional[str] = Field(default=None, description="HTTP method for delivery")
    status: Optional[str] = Field(default=None, description="Webhook status (active, inactive)")
    subscriptions: Optional[List[str]] = Field(default=None, description="Event subscriptions")
    request_format: Optional[str] = Field(default=None, description="Payload format")
    authentication: Optional[Dict[str, Any]] = Field(default=None, description="Authentication settings")
    created_at: Optional[datetime] = Field(default=None, description="When the webhook was created")
    updated_at: Optional[datetime] = Field(default=None, description="When the webhook was last updated")
