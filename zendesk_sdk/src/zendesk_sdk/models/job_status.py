"""Job status models for Zendesk async batch operations."""

from typing import Any, Dict, List, Optional

from pydantic import Field

from .base import ZendeskModel


class JobStatus(ZendeskModel):
    """Zendesk background job status."""

    id: Optional[str] = Field(default=None, description="The job ID")
    url: Optional[str] = Field(default=None, description="The API URL of the job")
    status: Optional[str] = Field(default=None, description="Job status (queued, working, completed, failed, killed)")
    message: Optional[str] = Field(default=None, description="Status message from Zendesk")
    progress: Optional[int] = Field(default=None, description="Number of items processed")
    total: Optional[int] = Field(default=None, description="Total number of items to process")
    results: Optional[List[Dict[str, Any]]] = Field(default=None, description="Per-item results when available")
