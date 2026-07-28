"""Zendesk API data models."""

from .audit import Audit, AuditEvent
from .base import ZendeskModel
from .brand import Brand
from .comment import Comment, CommentAttachment, CommentMetadata, CommentVia
from .custom_status import CustomStatus
from .enriched_ticket import EnrichedTicket
from .group import Group
from .group_membership import GroupMembership
from .help_center import Article, Category, Section
from .job_status import JobStatus
from .organization import Organization, OrganizationField, OrganizationSubscription
from .search import (
    SearchQueryConfig,
    SearchType,
    SortOrder,
    TicketChannel,
    TicketPriority,
    TicketPriorityInput,
    TicketPriorityLiteral,
    TicketStatus,
    TicketStatusInput,
    TicketStatusLiteral,
    TicketType,
    TicketTypeInput,
    TicketTypeLiteral,
    UserRole,
)
from .sla import SlaPolicy
from .ticket import (
    RequesterInput,
    SatisfactionRating,
    Ticket,
    TicketCustomField,
    TicketField,
    TicketMetrics,
    TicketVia,
)
from .ticket_form import TicketForm
from .trigger import Automation, RuleConditions, Trigger
from .user import PasswordRequirements, User, UserField, UserIdentity, UserPhoto
from .view import View, ViewCount
from .webhook import Webhook

__all__ = [
    "ZendeskModel",
    "User",
    "UserField",
    "UserIdentity",
    "UserPhoto",
    "PasswordRequirements",
    "Group",
    "GroupMembership",
    "Organization",
    "OrganizationField",
    "OrganizationSubscription",
    "Ticket",
    "TicketField",
    "TicketMetrics",
    "TicketCustomField",
    "TicketVia",
    "SatisfactionRating",
    "RequesterInput",
    "Audit",
    "AuditEvent",
    "TicketForm",
    "JobStatus",
    "CustomStatus",
    "Trigger",
    "Automation",
    "RuleConditions",
    "Webhook",
    "SlaPolicy",
    "Brand",
    "Comment",
    "CommentAttachment",
    "CommentMetadata",
    "CommentVia",
    "EnrichedTicket",
    "View",
    "ViewCount",
    "Category",
    "Section",
    "Article",
    "SearchQueryConfig",
    "SearchType",
    "TicketStatus",
    "TicketStatusLiteral",
    "TicketStatusInput",
    "TicketPriority",
    "TicketPriorityLiteral",
    "TicketPriorityInput",
    "TicketType",
    "TicketTypeLiteral",
    "TicketTypeInput",
    "TicketChannel",
    "UserRole",
    "SortOrder",
]
