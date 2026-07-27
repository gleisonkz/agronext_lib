"""SLA policy models for Zendesk API."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from .base import ZendeskModel


class SlaPolicy(ZendeskModel):
    """Zendesk SLA policy definition."""

    id: Optional[int] = Field(default=None, description="The SLA policy ID")
    url: Optional[str] = Field(default=None, description="The API URL of the policy")
    title: Optional[str] = Field(default=None, description="Policy title")
    description: Optional[str] = Field(default=None, description="Policy description")
    position: Optional[int] = Field(default=None, description="Relative position among policies")
    filter: Optional[Dict[str, Any]] = Field(default=None, description="Ticket filter for the policy")
    policy_metrics: Optional[List[Dict[str, Any]]] = Field(default=None, description="Metric targets for the policy")
    created_at: Optional[datetime] = Field(default=None, description="When the policy was created")
    updated_at: Optional[datetime] = Field(default=None, description="When the policy was last updated")
