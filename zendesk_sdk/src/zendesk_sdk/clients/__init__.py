"""Zendesk API clients."""

from .attachments import AttachmentsClient
from .automations import AutomationsClient
from .brands import BrandsClient
from .custom_statuses import CustomStatusesClient
from .groups import GroupsClient
from .help_center import ArticlesClient, CategoriesClient, HelpCenterClient, SectionsClient
from .incremental import IncrementalClient
from .job_statuses import JobStatusesClient
from .organizations import OrganizationsClient
from .search import SearchClient
from .sla_policies import SlaPoliciesClient
from .ticket_fields import TicketFieldsClient
from .ticket_forms import TicketFormsClient
from .ticket_metrics import TicketMetricsClient
from .tickets import AuditsClient, CommentsClient, TagsClient, TicketsClient
from .triggers import TriggersClient
from .users import UsersClient
from .views import ViewsClient
from .webhooks import WebhooksClient

__all__ = [
    "UsersClient",
    "GroupsClient",
    "OrganizationsClient",
    "TicketsClient",
    "TicketFieldsClient",
    "TicketFormsClient",
    "TicketMetricsClient",
    "JobStatusesClient",
    "CustomStatusesClient",
    "TriggersClient",
    "AutomationsClient",
    "WebhooksClient",
    "SlaPoliciesClient",
    "IncrementalClient",
    "BrandsClient",
    "AttachmentsClient",
    "SearchClient",
    "ViewsClient",
    "CommentsClient",
    "TagsClient",
    "AuditsClient",
    "HelpCenterClient",
    "CategoriesClient",
    "SectionsClient",
    "ArticlesClient",
]
