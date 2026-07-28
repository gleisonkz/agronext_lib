"""Trigger and automation models for Zendesk API."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from .base import ZendeskModel


class RuleConditions(ZendeskModel):
    """Conditions block shared by triggers and automations."""

    all: Optional[List[Dict[str, Any]]] = Field(default=None, description="All conditions must match")
    any: Optional[List[Dict[str, Any]]] = Field(default=None, description="Any condition may match")


class Trigger(ZendeskModel):
    """Zendesk trigger definition."""

    id: Optional[int] = Field(default=None, description="The trigger ID")
    url: Optional[str] = Field(default=None, description="The API URL of the trigger")
    title: Optional[str] = Field(default=None, description="Trigger title")
    active: Optional[bool] = Field(default=None, description="Whether the trigger is active")
    position: Optional[int] = Field(default=None, description="Execution order position")
    category_id: Optional[int] = Field(default=None, description="Trigger category ID")
    conditions: Optional[RuleConditions] = Field(default=None, description="Trigger conditions")
    actions: Optional[List[Dict[str, Any]]] = Field(default=None, description="Trigger actions")
    created_at: Optional[datetime] = Field(default=None, description="When the trigger was created")
    updated_at: Optional[datetime] = Field(default=None, description="When the trigger was last updated")


class Automation(ZendeskModel):
    """Zendesk automation definition."""

    id: Optional[int] = Field(default=None, description="The automation ID")
    url: Optional[str] = Field(default=None, description="The API URL of the automation")
    title: Optional[str] = Field(default=None, description="Automation title")
    active: Optional[bool] = Field(default=None, description="Whether the automation is active")
    position: Optional[int] = Field(default=None, description="Execution order position")
    conditions: Optional[RuleConditions] = Field(default=None, description="Automation conditions")
    actions: Optional[List[Dict[str, Any]]] = Field(default=None, description="Automation actions")
    created_at: Optional[datetime] = Field(default=None, description="When the automation was created")
    updated_at: Optional[datetime] = Field(default=None, description="When the automation was last updated")
