"""Tests for extended SDK clients (audits, forms, batch, admin APIs)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from zendesk_sdk.clients import (
    AuditsClient,
    AutomationsClient,
    CustomStatusesClient,
    IncrementalClient,
    JobStatusesClient,
    SlaPoliciesClient,
    TicketFieldsClient,
    TicketFormsClient,
    TriggersClient,
    WebhooksClient,
)
from zendesk_sdk.clients.tickets import CommentsClient, TicketsClient
from zendesk_sdk.exceptions import ZendeskTimeoutException, ZendeskValidationException
from zendesk_sdk.models import (
    Audit,
    Automation,
    CustomStatus,
    JobStatus,
    SlaPolicy,
    TicketField,
    TicketForm,
    Trigger,
    Webhook,
)


class TestTicketWriteParams:
    def get_client(self):
        return TicketsClient(MagicMock())

    @pytest.mark.asyncio
    async def test_create_with_requester_object(self):
        client = self.get_client()
        with patch.object(client, "_post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = {"ticket": {"id": 1, "subject": "Test", "status": "new"}}
            await client.create(
                "Help",
                subject="Test",
                requester={"name": "Jane", "email": "jane@example.com"},
                brand_id=10,
                ticket_form_id=20,
                custom_status_id=30,
            )
            payload = mock_post.call_args[1]["json"]["ticket"]
            assert payload["requester"] == {"name": "Jane", "email": "jane@example.com"}
            assert payload["brand_id"] == 10
            assert payload["ticket_form_id"] == 20
            assert payload["custom_status_id"] == 30

    @pytest.mark.asyncio
    async def test_create_rejects_requester_and_requester_id(self):
        client = self.get_client()
        with pytest.raises(ZendeskValidationException):
            await client.create("Help", requester={"email": "a@b.com"}, requester_id=123)

    @pytest.mark.asyncio
    async def test_update_custom_status_id(self):
        client = self.get_client()
        with patch.object(client, "_put", new_callable=AsyncMock) as mock_put:
            mock_put.return_value = {"ticket": {"id": 1, "status": "open", "custom_status_id": 99}}
            await client.update(1, custom_status_id=99, ticket_form_id=5, brand_id=2)
            payload = mock_put.call_args[1]["json"]["ticket"]
            assert payload["custom_status_id"] == 99
            assert payload["ticket_form_id"] == 5
            assert payload["brand_id"] == 2


class TestAuditsClient:
    def get_client(self):
        return AuditsClient(MagicMock())

    def test_list_returns_paginator(self):
        client = self.get_client()
        paginator = client.list(123, filter_events=["Change"])
        assert paginator.path == "tickets/123/audits.json"
        assert paginator._filter_events == ["Change"]

    def test_filter_events_by_type(self):
        audit = Audit(
            id=1,
            events=[
                {"type": "Change", "field_name": "status", "previous_value": "open", "value": "pending"},
                {"type": "Comment", "body": "note"},
            ],
        )
        filtered = AuditsClient.filter_events_by_type([audit], ["status"])
        assert len(filtered) == 1
        assert len(filtered[0].events or []) == 1
        assert filtered[0].events[0].field_name == "status"


class TestCommentRedactions:
    def get_client(self):
        return CommentsClient(MagicMock())

    @pytest.mark.asyncio
    async def test_redact_text_uses_legacy_endpoint(self):
        client = self.get_client()
        with patch.object(client, "_put", new_callable=AsyncMock) as mock_put:
            mock_put.return_value = {"comment": {"id": 11, "body": "redacted"}}
            await client.redact(1, 11, "secret")
            mock_put.assert_called_once_with(
                "tickets/1/comments/11/redact.json",
                json={"text": "secret"},
            )

    @pytest.mark.asyncio
    async def test_redact_html_uses_comment_redactions_endpoint(self):
        client = self.get_client()
        with patch.object(client, "_put", new_callable=AsyncMock) as mock_put:
            mock_put.return_value = {"comment": {"id": 11, "body": "redacted"}}
            await client.redact_html(1, 11, "<redact>secret</redact>")
            mock_put.assert_called_once_with(
                "comment_redactions/11.json",
                json={"ticket_id": 1, "html_body": "<redact>secret</redact>"},
            )

    @pytest.mark.asyncio
    async def test_redact_attachments(self):
        client = self.get_client()
        with patch.object(client, "_put", new_callable=AsyncMock) as mock_put:
            mock_put.return_value = {"comment": {"id": 11, "body": "redacted"}}
            urls = ["https://example.com/file.pdf"]
            await client.redact_attachments(1, 11, urls)
            mock_put.assert_called_once_with(
                "comment_redactions/11.json",
                json={"ticket_id": 1, "external_attachment_urls": urls},
            )


class TestTicketFieldsAdmin:
    def get_client(self):
        return TicketFieldsClient(MagicMock())

    @pytest.mark.asyncio
    async def test_create_invalidates_cache(self):
        client = self.get_client()
        client.get = MagicMock(cache_clear=MagicMock())
        with patch.object(client, "_post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = {"ticket_field": {"id": 1, "type": "text", "title": "Field"}}
            result = await client.create("Field", "text")
            assert isinstance(result, TicketField)
            client.get.cache_clear.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_and_delete_invalidate_cache(self):
        client = self.get_client()
        client.get = MagicMock(cache_clear=MagicMock())
        with patch.object(client, "_put", new_callable=AsyncMock) as mock_put:
            mock_put.return_value = {"ticket_field": {"id": 1, "type": "text", "title": "Updated"}}
            await client.update(1, title="Updated")
        with patch.object(client, "_delete", new_callable=AsyncMock):
            await client.delete(1)
        assert client.get.cache_clear.call_count == 2


class TestTicketFormsClient:
    def get_client(self):
        return TicketFormsClient(MagicMock())

    @pytest.mark.asyncio
    async def test_create(self):
        client = self.get_client()
        with patch.object(client, "_post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = {"ticket_form": {"id": 1, "name": "Support Form"}}
            result = await client.create("Support Form", display_name="Support", ticket_field_ids=[1, 2])
            assert isinstance(result, TicketForm)
            payload = mock_post.call_args[1]["json"]["ticket_form"]
            assert payload["ticket_field_ids"] == [1, 2]


class TestBatchAndJobStatuses:
    def get_tickets_client(self):
        return TicketsClient(MagicMock())

    def get_jobs_client(self):
        return JobStatusesClient(MagicMock())

    @pytest.mark.asyncio
    async def test_update_many(self):
        client = self.get_tickets_client()
        with patch.object(client, "_put", new_callable=AsyncMock) as mock_put:
            mock_put.return_value = {"job_status": {"id": "abc", "status": "queued"}}
            result = await client.update_many([1, 2], status="closed")
            assert isinstance(result, JobStatus)
            assert "tickets/update_many.json?ids=1,2" in mock_put.call_args[0][0]

    @pytest.mark.asyncio
    async def test_update_many_empty_raises(self):
        client = self.get_tickets_client()
        with pytest.raises(ZendeskValidationException):
            await client.update_many([], status="closed")

    @pytest.mark.asyncio
    async def test_wait_until_done_completed(self):
        client = self.get_jobs_client()
        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = [
                JobStatus(id="abc", status="working"),
                JobStatus(id="abc", status="completed"),
            ]
            result = await client.wait_until_done("abc", timeout=5, interval=0)
            assert result.status == "completed"

    @pytest.mark.asyncio
    async def test_wait_until_done_timeout(self):
        client = self.get_jobs_client()
        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = JobStatus(id="abc", status="working")
            with pytest.raises(ZendeskTimeoutException):
                await client.wait_until_done("abc", timeout=0, interval=0)


class TestCustomStatusesClient:
    @pytest.mark.asyncio
    async def test_get(self):
        client = CustomStatusesClient(MagicMock())
        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"custom_status": {"id": 1, "agent_label": "Waiting"}}
            result = await client.get(1)
            assert isinstance(result, CustomStatus)


class TestTriggersClient:
    @pytest.mark.asyncio
    async def test_update_active_flag(self):
        client = TriggersClient(MagicMock())
        with patch.object(client, "_put", new_callable=AsyncMock) as mock_put:
            mock_put.return_value = {"trigger": {"id": 1, "title": "Notify", "active": False}}
            result = await client.update(1, active=False)
            assert isinstance(result, Trigger)
            assert result.active is False


class TestAutomationsClient:
    @pytest.mark.asyncio
    async def test_get(self):
        client = AutomationsClient(MagicMock())
        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"automation": {"id": 1, "title": "Auto close"}}
            result = await client.get(1)
            assert isinstance(result, Automation)


class TestWebhooksClient:
    def test_list_uses_webhooks_path_without_json(self):
        client = WebhooksClient(MagicMock())
        paginator = client.list()
        assert paginator.path == "webhooks"

    @pytest.mark.asyncio
    async def test_create(self):
        client = WebhooksClient(MagicMock())
        with patch.object(client, "_post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = {"webhook": {"id": "wh1", "name": "Events"}}
            result = await client.create(
                "Events",
                endpoint="https://example.com/hook",
                subscriptions=["zen:event-type:ticket.created"],
            )
            assert isinstance(result, Webhook)
            mock_post.assert_called_once()
            assert mock_post.call_args[0][0] == "webhooks"

    @pytest.mark.asyncio
    async def test_get_path_without_json(self):
        client = WebhooksClient(MagicMock())
        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"webhook": {"id": "wh1", "name": "Events"}}
            await client.get("wh1")
            mock_get.assert_called_once_with("webhooks/wh1")


class TestBrandsClient:
    def test_list_path(self):
        from zendesk_sdk.clients import BrandsClient

        client = BrandsClient(MagicMock())
        paginator = client.list()
        assert paginator.path == "brands.json"

    @pytest.mark.asyncio
    async def test_get(self):
        from zendesk_sdk.clients import BrandsClient
        from zendesk_sdk.models import Brand

        client = BrandsClient(MagicMock())
        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"brand": {"id": 1, "name": "Main", "default": True}}
            result = await client.get(1)
            assert isinstance(result, Brand)
            assert result.name == "Main"


class TestSlaPoliciesClient:
    @pytest.mark.asyncio
    async def test_list_returns_paginator(self):
        client = SlaPoliciesClient(MagicMock())
        paginator = client.list()
        assert paginator.path == "slas/policies.json"

    @pytest.mark.asyncio
    async def test_get(self):
        client = SlaPoliciesClient(MagicMock())
        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"sla_policy": {"id": 1, "title": "Gold SLA"}}
            result = await client.get(1)
            assert isinstance(result, SlaPolicy)


class TestIncrementalClient:
    def test_ticket_events_paginator(self):
        client = IncrementalClient(MagicMock())
        paginator = client.ticket_events(1700000000)
        assert paginator.path == "incremental/ticket_events.json"

    def test_ticket_metric_events_paginator(self):
        client = IncrementalClient(MagicMock())
        paginator = client.ticket_metric_events(1700000000)
        assert paginator.path == "incremental/ticket_metric_events.json"
