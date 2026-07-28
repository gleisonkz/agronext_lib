"""Job Statuses API client."""

import asyncio
from typing import TYPE_CHECKING, Optional

from ..exceptions import ZendeskTimeoutException
from ..models.job_status import JobStatus
from .base import BaseClient

if TYPE_CHECKING:
    from ..http_client import HTTPClient

_TERMINAL_STATUSES = frozenset({"completed", "failed", "killed"})


class JobStatusesClient(BaseClient):
    """Client for Zendesk Job Statuses API."""

    async def get(self, job_id: str) -> JobStatus:
        """Get a job status by ID."""
        response = await self._get(f"job_statuses/{job_id}.json")
        return JobStatus(**response["job_status"])

    async def wait_until_done(
        self,
        job_id: str,
        *,
        timeout: float = 90.0,
        interval: float = 2.0,
    ) -> JobStatus:
        """Poll a job until it completes, fails, or times out."""
        loop = asyncio.get_event_loop()
        deadline = loop.time() + timeout
        last_status: Optional[JobStatus] = None

        while loop.time() < deadline:
            last_status = await self.get(job_id)
            if last_status.status in _TERMINAL_STATUSES:
                return last_status
            await asyncio.sleep(interval)

        raise ZendeskTimeoutException(
            f"Job {job_id} did not complete within {timeout}s (last status: {last_status.status if last_status else 'unknown'})",
            timeout=timeout,
        )
