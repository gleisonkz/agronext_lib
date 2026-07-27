"""Optional integration smoke tests against Essor Zendesk (skipped by default)."""

import os

import pytest

from zendesk_sdk import ZendeskClient, ZendeskConfig


def _integration_config():
    subdomain = os.getenv("ZENDESK_SUBDOMAIN")
    email = os.getenv("ZENDESK_EMAIL")
    token = os.getenv("ZENDESK_TOKEN")
    if not all([subdomain, email, token]):
        return None
    return ZendeskConfig(subdomain=subdomain, email=email, token=token)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_list_ticket_fields_smoke():
    config = _integration_config()
    if config is None:
        pytest.skip("Set ZENDESK_SUBDOMAIN, ZENDESK_EMAIL, and ZENDESK_TOKEN for integration tests")

    async with ZendeskClient(config) as client:
        fields = [field async for field in client.ticket_fields.list(limit=1)]
        assert isinstance(fields, list)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_list_custom_statuses_smoke():
    config = _integration_config()
    if config is None:
        pytest.skip("Set ZENDESK_SUBDOMAIN, ZENDESK_EMAIL, and ZENDESK_TOKEN for integration tests")

    async with ZendeskClient(config) as client:
        statuses = [status async for status in client.custom_statuses.list(limit=1)]
        assert isinstance(statuses, list)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_list_webhooks_smoke():
    config = _integration_config()
    if config is None:
        pytest.skip("Set ZENDESK_SUBDOMAIN, ZENDESK_EMAIL, and ZENDESK_TOKEN for integration tests")

    async with ZendeskClient(config) as client:
        hooks = [hook async for hook in client.webhooks.list(limit=1)]
        assert isinstance(hooks, list)
