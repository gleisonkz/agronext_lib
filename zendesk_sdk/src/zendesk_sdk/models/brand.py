"""Brand model for Zendesk API."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from .base import ZendeskModel


class Brand(ZendeskModel):
    """Zendesk brand (multi-brand accounts)."""

    id: Optional[int] = Field(default=None, description="Automatically assigned when the brand is created")
    url: Optional[str] = Field(default=None, description="The API URL of this brand")
    name: Optional[str] = Field(default=None, description="The name of the brand")
    brand_url: Optional[str] = Field(default=None, description="The URL of the brand")
    subdomain: Optional[str] = Field(default=None, description="The subdomain of the brand")
    host_mapping: Optional[str] = Field(default=None, description="Custom domain host mapping")
    has_help_center: Optional[bool] = Field(default=None, description="If true, the brand has a Help Center")
    help_center_state: Optional[str] = Field(default=None, description="Help Center state")
    active: Optional[bool] = Field(default=None, description="If the brand is active")
    default: Optional[bool] = Field(default=None, description="If this is the default brand")
    is_deleted: Optional[bool] = Field(default=None, description="If the brand is deleted")
    logo: Optional[Dict[str, Any]] = Field(default=None, description="Logo attachment object")
    ticket_form_ids: Optional[List[int]] = Field(default=None, description="Ticket form ids for the brand")
    created_at: Optional[datetime] = Field(default=None, description="When the brand was created")
    updated_at: Optional[datetime] = Field(default=None, description="When the brand was last updated")
