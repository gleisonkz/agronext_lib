"""Async API usage example mirroring ``poc_zendesk.py`` with the typed SDK.

Exercises the full POC/checklist surface available in the SDK:
tickets (create/update/assign/transfer/close/list/get_many/enriched),
comments, tags, audits, attachments + redactions, custom fields/forms,
approvals, brands, custom statuses, users/orgs CRUD, triggers/automations,
webhooks, SLA, metrics, views, help center, search, incremental exports,
and batch jobs.

Status-transition business rules are **caller-owned**.

Prerequisites:
  - Copy ``.env.example`` to ``.env`` and fill credentials / POC field IDs
  - ``pip install -e ".[dev]"`` (needs ``python-dotenv``)

Run:
  uv run python examples/api_usage_example.py
  uv run python examples/api_usage_example.py --interactive
  uv run python examples/api_usage_example.py --skip-close
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None  # type: ignore[assignment]

from zendesk_sdk import ZendeskClient, ZendeskConfig
from zendesk_sdk.exceptions import ZendeskHTTPException, ZendeskPaginationException
from zendesk_sdk.models import Group, Ticket, User

ROOT = Path(__file__).resolve().parents[1]
if load_dotenv is not None:
    load_dotenv(ROOT / ".env")

POC_TAG = "poc_zendesk"
POC_TAG_SDK = "poc_zendesk_sdk_async"


def _env_int(name: str, default: int = 0) -> int:
    raw = os.getenv(name, str(default)).strip()
    try:
        return int(raw) if raw else default
    except ValueError:
        return default


def _env_str(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


FIELD_APROVACAO_SIMPLES = _env_int("ZENDESK_FIELD_APROVACAO_SIMPLES")
FIELD_APROVACAO_DUPLA = _env_int("ZENDESK_FIELD_APROVACAO_DUPLA")
FIELD_APROVACAO_NIVEL = _env_int("ZENDESK_FIELD_APROVACAO_NIVEL")
FORM_POC = _env_int("ZENDESK_FORM_POC")
FIELD_PRODUTO = _env_int("ZENDESK_FIELD_PRODUTO")
FIELD_TIPO_CHAMADO = _env_int("ZENDESK_FIELD_TIPO_CHAMADO")
FIELD_PROPOSTA = _env_int("ZENDESK_FIELD_PROPOSTA")
FIELD_PRODUTO_VALOR = _env_str("ZENDESK_FIELD_PRODUTO_VALOR", "agrícola_")
FIELD_TIPO_CHAMADO_VALOR = _env_str("ZENDESK_FIELD_TIPO_CHAMADO_VALOR", "poc_agronext_suporte")

# Optional fixed IDs for non-interactive runs
ENV_REQUESTER_ID = _env_int("ZENDESK_EXAMPLE_REQUESTER_ID")
ENV_ASSIGNEE_ID = _env_int("ZENDESK_EXAMPLE_ASSIGNEE_ID")
ENV_GROUP_ID = _env_int("ZENDESK_EXAMPLE_GROUP_ID")
ENV_TRANSFER_ASSIGNEE_ID = _env_int("ZENDESK_EXAMPLE_TRANSFER_ASSIGNEE_ID")
ENV_TRANSFER_GROUP_ID = _env_int("ZENDESK_EXAMPLE_TRANSFER_GROUP_ID")


def ticket_url(subdomain: str, ticket_id: int) -> str:
    return f"https://{subdomain}.zendesk.com/agent/tickets/{ticket_id}"


def prompt_continue(title: str, *, interactive: bool, ticket_id: Optional[int] = None) -> bool:
    """In interactive mode, pause between steps. Otherwise always continue."""
    print(f"\n{'=' * 60}")
    print(f"NEXT: {title}")
    if ticket_id:
        print(f"  Ticket #{ticket_id}")
    if not interactive:
        return True
    while True:
        answer = input("  [Enter]=run | s=skip | q=quit: ").strip().lower()
        if answer == "q":
            raise SystemExit(0)
        if answer == "s":
            print("  -> skipped")
            return False
        return True


def opening_custom_fields() -> List[Dict[str, Any]]:
    fields: List[Dict[str, Any]] = []
    if FIELD_PRODUTO and FIELD_PRODUTO_VALOR:
        fields.append({"id": FIELD_PRODUTO, "value": FIELD_PRODUTO_VALOR})
    if FIELD_TIPO_CHAMADO and FIELD_TIPO_CHAMADO_VALOR:
        fields.append({"id": FIELD_TIPO_CHAMADO, "value": FIELD_TIPO_CHAMADO_VALOR})
    return fields


async def list_possible_requesters(
    client: ZendeskClient,
    *,
    query: Optional[str] = None,
    limit: int = 200,
) -> List[User]:
    """List users that can be ticket requesters.

    Default path uses ``users.list`` (full Users API), which is much more
    complete than Search ``role:`` queries on small/trial accounts.
    Optional ``query`` filters locally first, then falls back to Search API.
    """
    if query:
        q = query.strip()
        if "@" in q:
            by_email = await client.users.by_email(q)
            if by_email:
                return [by_email]
        # Broad list then local filter (name/email/id)
        pool = await client.users.list(per_page=100, limit=limit).collect()
        q_lower = q.lower()
        local = [
            u
            for u in pool
            if q_lower in (u.name or "").lower()
            or q_lower in (u.email or "").lower()
            or q_lower == str(u.id)
        ]
        if local:
            return [u for u in local if u.active is not False]
        return await client.search.users(q, limit=min(limit, 50)).collect()

    users = await client.users.list(per_page=100, limit=limit).collect()
    return [u for u in users if u.active is not False]


def _format_user(user: User) -> str:
    email = user.email or "-"
    role = user.role or "-"
    return f"{user.name} <{email}> (id={user.id}, role={role})"


def _print_requester_page(candidates: List[User], me: User, page: int, page_size: int = 25) -> int:
    """Print one page of requesters. Returns total pages."""
    total = len(candidates)
    pages = max(1, (total + page_size - 1) // page_size)
    page = max(0, min(page, pages - 1))
    start = page * page_size
    chunk = candidates[start : start + page_size]
    print(f"  Possible requesters ({total} users) — page {page + 1}/{pages}:")
    for i, user in enumerate(chunk, start=start + 1):
        marker = " [you]" if user.id == me.id else ""
        print(f"    {i}. {_format_user(user)}{marker}")
    if pages > 1:
        print("  Tip: type n/p for next/prev page, or a name/email to filter.")
    return pages


async def pick_requester(client: ZendeskClient, interactive: bool) -> User:
    if ENV_REQUESTER_ID:
        return await client.users.get(ENV_REQUESTER_ID)

    me = await client.users.me()
    if not interactive:
        return me

    print("\n  Loading users from Users API (can be requesters)...")
    candidates = await list_possible_requesters(client, limit=200)
    candidates.sort(key=lambda u: ((u.name or "").lower(), u.id or 0))
    # Keep "me" visible at the top when present
    if me.id:
        candidates = [me] + [u for u in candidates if u.id != me.id]

    page = 0
    page_size = 25
    while True:
        if not candidates:
            print("  No users found. Try another filter (name/email) or Enter to use me.")
        else:
            pages = _print_requester_page(candidates, me, page, page_size=page_size)
        raw = input(
            "  Pick index, n/p page, name/email filter, or Enter = me: "
        ).strip()
        if not raw:
            return me
        low = raw.lower()
        if low in {"n", "next"} and candidates:
            page = min(page + 1, max(0, (len(candidates) - 1) // page_size))
            continue
        if low in {"p", "prev", "previous"} and candidates:
            page = max(page - 1, 0)
            continue
        if raw.isdigit():
            idx = int(raw)
            if 1 <= idx <= len(candidates):
                return candidates[idx - 1]
            print(f"  Invalid index (1-{len(candidates)})")
            continue
        # Filter / search by free text
        candidates = await list_possible_requesters(client, query=raw, limit=200)
        candidates.sort(key=lambda u: ((u.name or "").lower(), u.id or 0))
        page = 0
        if len(candidates) == 1:
            print(f"  Matched: {_format_user(candidates[0])}")
            return candidates[0]
        if not candidates:
            print(f"  No match for {raw!r}")


async def list_assignable_groups(client: ZendeskClient) -> List[Group]:
    groups = await client.groups.list_assignable(limit=100).collect()
    if not groups:
        groups = await client.groups.list(limit=100).collect()
    if not groups:
        raise RuntimeError("No groups found — create a group in Zendesk first.")
    return groups


async def list_agents_in_group(client: ZendeskClient, group_id: int) -> List[User]:
    """Return users who are members of ``group_id`` (required for ticket assignment)."""
    memberships = await client.groups.list_group_members(group_id).collect()
    user_ids = [m.user_id for m in memberships if m.user_id]
    if not user_ids:
        return []
    users_by_id = await client.users.get_many(user_ids)
    # Preserve membership order; skip missing/deleted users
    agents: List[User] = []
    for uid in user_ids:
        user = users_by_id.get(uid)
        if user is None:
            continue
        # Light agents / end-users cannot be ticket assignees in most plans
        role = (user.role or "").lower()
        if role in {"end-user", "end_user"}:
            continue
        agents.append(user)
    return agents


def _prompt_index(label: str, count: int, default: int = 1) -> int:
    raw = input(f"  {label} [{default}]: ").strip() or str(default)
    idx = int(raw)
    if idx < 1 or idx > count:
        raise ValueError(f"Index must be between 1 and {count}")
    return idx


async def pick_group_then_assignee(
    client: ZendeskClient,
    interactive: bool,
    *,
    title: str = "assignment",
    preferred_group_id: Optional[int] = None,
    preferred_assignee_id: Optional[int] = None,
    exclude_group_id: Optional[int] = None,
    exclude_assignee_id: Optional[int] = None,
) -> tuple[Group, User]:
    """Pick group first, then an agent who belongs to that group.

    Zendesk rejects assignee_id unless the agent is a member of group_id.
    """
    groups = await list_assignable_groups(client)
    if exclude_group_id is not None:
        filtered = [g for g in groups if g.id != exclude_group_id]
        if filtered:
            groups = filtered

    group: Optional[Group] = None
    if preferred_group_id:
        group = next((g for g in groups if g.id == preferred_group_id), None)
        if group is None:
            group = await client.groups.get(preferred_group_id)

    if group is None:
        if not interactive:
            # Non-interactive: first group that has at least one assignable member
            for candidate in groups:
                assert candidate.id is not None
                members = await list_agents_in_group(client, candidate.id)
                if members:
                    group = candidate
                    break
            if group is None:
                raise RuntimeError("No assignable group with members found.")
        else:
            print(f"\n  Select group for {title} (assignee must belong to this group):")
            for i, g in enumerate(groups[:20], 1):
                print(f"    {i}. {g.name} (id={g.id})")
            gi = _prompt_index("Group index", min(len(groups), 20))
            group = groups[gi - 1]

    assert group.id is not None
    members = await list_agents_in_group(client, group.id)
    if exclude_assignee_id is not None:
        members = [u for u in members if u.id != exclude_assignee_id]
    if not members:
        raise RuntimeError(
            f"Group «{group.name}» (id={group.id}) has no assignable agents. "
            "Add an agent to this group in Zendesk Admin, then retry."
        )

    assignee: Optional[User] = None
    if preferred_assignee_id:
        assignee = next((u for u in members if u.id == preferred_assignee_id), None)
        if assignee is None:
            raise RuntimeError(
                f"User id={preferred_assignee_id} is not a member of group "
                f"«{group.name}» (id={group.id}). Pick a member of that group."
            )

    if assignee is None:
        if not interactive:
            assignee = members[0]
        else:
            print(f"\n  Select agent in group «{group.name}»:")
            for i, user in enumerate(members[:20], 1):
                print(f"    {i}. {user.name} <{user.email}> (id={user.id}, role={user.role})")
            ai = _prompt_index("Agent index", min(len(members), 20))
            assignee = members[ai - 1]

    return group, assignee


async def set_custom_field(client: ZendeskClient, ticket_id: int, field_id: int, value: Any) -> Ticket:
    return await client.tickets.update(
        ticket_id,
        custom_fields=[{"id": field_id, "value": value}],
    )


def field_value(ticket: Ticket, field_id: int) -> Any:
    return ticket.get_custom_field_value(field_id)


async def demo_brands_and_ticket_params(
    client: ZendeskClient,
    *,
    interactive: bool,
    ticket_id: int,
    requester: User,
    created_ids: List[int],
) -> Optional[int]:
    """I01 — list/get brands and set brand_id / custom_status_id on the ticket."""
    if not prompt_continue(
        "[I01] Brands + typed ticket params (brand_id / custom_status_id)",
        interactive=interactive,
        ticket_id=ticket_id,
    ):
        return None

    brand_id: Optional[int] = None
    try:
        brands = await client.brands.list(limit=20).collect()
        print(f"  Brands: {len(brands)}")
        for brand in brands[:8]:
            print(
                f"    - id={brand.id} name={brand.name} "
                f"default={brand.default} active={brand.active}"
            )
        chosen = next((b for b in brands if b.default and b.id), None) or (
            brands[0] if brands else None
        )
        brand_id = chosen.id if chosen else None
        if brand_id:
            brand = await client.brands.get(brand_id)
            print(f"  brands.get({brand_id}): name={brand.name} subdomain={brand.subdomain}")
    except (ZendeskHTTPException, ZendeskPaginationException) as exc:
        print(f"  Brands unavailable: {exc}")

    custom_status_id: Optional[int] = None
    status_category: Optional[str] = None
    try:
        statuses = await client.custom_statuses.list(limit=20).collect()
        print(f"  Custom statuses: {len(statuses)}")
        for st in statuses[:6]:
            print(
                f"    - id={st.id} agent_label={st.agent_label} "
                f"category={st.status_category}"
            )
        pick = next(
            (s for s in statuses if (s.status_category or "") == "pending" and s.id),
            None,
        ) or next((s for s in statuses if s.id), None)
        if pick and pick.id:
            custom_status_id = pick.id
            status_category = pick.status_category
            st = await client.custom_statuses.get(pick.id)
            print(f"  custom_statuses.get({pick.id}): {st.agent_label}")
    except (ZendeskHTTPException, ZendeskPaginationException) as exc:
        print(f"  Custom statuses unavailable: {exc}")

    update_kwargs: Dict[str, Any] = {}
    if brand_id:
        update_kwargs["brand_id"] = brand_id
    if custom_status_id:
        update_kwargs["custom_status_id"] = custom_status_id
        if status_category:
            update_kwargs["status"] = status_category
    if update_kwargs:
        ticket = await client.tickets.update(ticket_id, **update_kwargs)
        print(
            f"  Updated ticket brand_id={ticket.brand_id} "
            f"custom_status_id={ticket.custom_status_id} status={ticket.status}"
        )
    else:
        print("  No brand_id/custom_status_id available to set")

    if requester.email and prompt_continue(
        "[T01] Create aux ticket with requester={name,email} object",
        interactive=interactive,
        ticket_id=ticket_id,
    ):
        aux = await client.tickets.create(
            comment_body="Created with requester object (not only requester_id).",
            subject="[SDK-ASYNC][T01] requester object",
            requester={"name": requester.name or "Requester", "email": requester.email},
            tags=[POC_TAG_SDK, "t01_requester_object"],
            brand_id=brand_id,
            public=False,
        )
        assert aux.id is not None
        created_ids.append(aux.id)
        print(f"  Aux ticket #{aux.id} requester_id={aux.requester_id}")

    return brand_id


async def demo_admin_catalog(client: ZendeskClient, *, interactive: bool, ticket_id: int) -> None:
    """Showcase admin/read APIs used by the checklist."""
    if not prompt_continue(
        "Admin/read APIs (fields, forms, triggers, automations, views, orgs, HC, incremental…)",
        interactive=interactive,
        ticket_id=ticket_id,
    ):
        return

    fields = await client.ticket_fields.list(limit=15).collect()
    print(f"  Ticket fields (sample): {len(fields)}")
    for field in fields[:5]:
        print(f"    - id={field.id} type={field.type} title={field.title}")
    if fields and fields[0].title:
        by_title = await client.ticket_fields.get_by_title(fields[0].title)
        print(f"  get_by_title({fields[0].title!r}): id={by_title.id if by_title else None}")

    forms = await client.ticket_forms.list(limit=15).collect()
    print(f"  Ticket forms: {len(forms)}")
    for form in forms[:5]:
        print(f"    - id={form.id} name={form.name} active={form.active}")
    if FORM_POC:
        form = await client.ticket_forms.get(FORM_POC)
        print(f"  FORM_POC get: id={form.id} fields={len(form.ticket_field_ids or [])}")

    triggers = await client.triggers.list(limit=10).collect()
    print(f"  Triggers: {len(triggers)}")
    if triggers and triggers[0].id:
        trig = await client.triggers.get(triggers[0].id)
        print(f"  triggers.get: id={trig.id} title={trig.title}")

    automations = await client.automations.list(limit=10).collect()
    print(f"  Automations: {len(automations)}")
    if automations and automations[0].id:
        auto = await client.automations.get(automations[0].id)
        print(f"  automations.get: id={auto.id} title={auto.title}")

    try:
        hooks = await client.webhooks.list(limit=10).collect()
        print(f"  Webhooks: {len(hooks)}")
        if hooks and hooks[0].id:
            hook = await client.webhooks.get(hooks[0].id)
            print(f"  webhooks.get: id={hook.id} name={hook.name}")
    except (ZendeskHTTPException, ZendeskPaginationException) as exc:
        print(f"  Webhooks unavailable: {exc}")

    try:
        policies = await client.sla_policies.list(limit=10).collect()
        print(f"  SLA policies: {len(policies)}")
        if policies and policies[0].id:
            pol = await client.sla_policies.get(policies[0].id)
            print(f"  sla_policies.get: id={pol.id} title={pol.title}")
    except (ZendeskHTTPException, ZendeskPaginationException) as exc:
        print(f"  SLA policies unavailable: {exc}")

    metrics = await client.ticket_metrics.for_ticket(ticket_id)
    print(f"  Ticket metrics reply_time={metrics.reply_time_in_minutes}")
    try:
        metric_rows = await client.ticket_metrics.list(limit=3).collect()
        print(f"  ticket_metrics.list sample: {len(metric_rows)}")
        if metrics.id:
            one = await client.ticket_metrics.get(metrics.id)
            print(f"  ticket_metrics.get({metrics.id}): ticket_id={one.ticket_id}")
    except (ZendeskHTTPException, ZendeskPaginationException) as exc:
        print(f"  ticket_metrics list/get skipped: {exc}")

    views = await client.views.list(limit=10).collect()
    print(f"  Views: {len(views)}")
    if views and views[0].id:
        try:
            count = await client.views.count(views[0].id)
            print(f"  View #{views[0].id} count={count.value} fresh={count.fresh}")
            view_ids = [v.id for v in views[:3] if v.id]
            if view_ids:
                many = await client.views.get_many(view_ids)
                print(f"  views.get_many: {len(many)} views")
                counts = await client.views.count_many(view_ids)
                print(f"  views.count_many: {len(counts)} counts")
            view_tickets = await client.views.tickets(views[0].id, limit=3).collect()
            print(f"  views.tickets sample: {len(view_tickets)}")
        except ZendeskHTTPException as exc:
            print(f"  View details unavailable: {exc}")

    try:
        gcount = await client.groups.count()
        print(f"  groups.count: {gcount}")
    except ZendeskHTTPException as exc:
        print(f"  groups.count unavailable: {exc}")

    orgs = await client.organizations.list(limit=5).collect()
    print(f"  Organizations (sample): {len(orgs)}")

    try:
        categories = await client.help_center.categories.list(limit=5).collect()
        print(f"  Help Center categories: {len(categories)}")
        sections = await client.help_center.sections.list(limit=5).collect()
        print(f"  Help Center sections: {len(sections)}")
        articles = await client.help_center.articles.list(limit=5).collect()
        print(f"  Help Center articles: {len(articles)}")
        found_articles = await client.help_center.articles.search("zendesk", per_page=3)
        print(f"  Help Center article search: {len(found_articles)}")
    except (ZendeskHTTPException, ZendeskPaginationException) as exc:
        print(f"  Help Center unavailable: {exc}")

    start_time = int(datetime.now(timezone.utc).timestamp()) - 7 * 24 * 3600
    try:
        events = await client.incremental.ticket_events(start_time=start_time, limit=5).collect()
        print(f"  Incremental ticket_events (sample): {len(events)}")
    except (ZendeskHTTPException, ZendeskPaginationException) as exc:
        print(f"  Incremental ticket_events unavailable: {exc}")
    try:
        metric_events = await client.incremental.ticket_metric_events(
            start_time=start_time, limit=5
        ).collect()
        print(f"  Incremental ticket_metric_events (sample): {len(metric_events)}")
    except (ZendeskHTTPException, ZendeskPaginationException) as exc:
        print(f"  Incremental ticket_metric_events unavailable: {exc}")

    found = 0
    async for hit in client.search.tickets(f"tags:{POC_TAG_SDK}", limit=5):
        found += 1
        print(f"  Search tickets: #{hit.id} {hit.subject}")
    print(f"  Search tickets hits: {found}")
    try:
        users_found = await client.search.users("type:user", limit=3).collect()
        print(f"  Search users: {len(users_found)}")
        orgs_found = await client.search.organizations("type:organization", limit=3).collect()
        print(f"  Search organizations: {len(orgs_found)}")
        mixed = 0
        async for _ in client.search.all(f"tags:{POC_TAG_SDK}", limit=3):
            mixed += 1
        print(f"  Search all (mixed): {mixed}")
    except (ZendeskHTTPException, ZendeskPaginationException) as exc:
        print(f"  Extra search demos skipped: {exc}")


async def demo_ticket_fields_crud(client: ZendeskClient, *, interactive: bool, ticket_id: int) -> None:
    """F01 — create/update/delete a temporary custom field (cleanup after)."""
    if not prompt_continue(
        "[F01] Ticket fields CRUD (temporary field create/update/delete)",
        interactive=interactive,
        ticket_id=ticket_id,
    ):
        return

    title = f"[SDK-ASYNC] temp field {datetime.now(timezone.utc).strftime('%H%M%S')}"
    try:
        field = await client.ticket_fields.create(
            title,
            "text",
            description="Temporary field from api_usage_example — safe to delete",
            visible_in_portal=False,
        )
        assert field.id is not None
        print(f"  Created field id={field.id} title={field.title}")
        updated = await client.ticket_fields.update(
            field.id, description="Updated by api_usage_example"
        )
        print(f"  Updated description={updated.description!r}")
        await client.ticket_fields.delete(field.id)
        print(f"  Deleted field id={field.id}")
    except ZendeskHTTPException as exc:
        print(f"  Ticket fields CRUD failed (permissions?): {exc}")


async def demo_users_and_orgs(client: ZendeskClient, *, interactive: bool, ticket_id: int) -> None:
    """U03 + orgs — temporary end-user and organization with cleanup."""
    if not prompt_continue(
        "[U03] Users + organizations CRUD (temporary resources, cleaned up)",
        interactive=interactive,
        ticket_id=ticket_id,
    ):
        return

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    email = f"sdk.async.demo+{stamp}@example.com"
    try:
        user = await client.users.create(
            name=f"[SDK-ASYNC] Demo User {stamp}",
            email=email,
            role="end-user",
            verified=True,
        )
        assert user.id is not None
        print(f"  Created end-user id={user.id} email={user.email}")
        user = await client.users.update(user.id, notes="Updated by api_usage_example")
        print(f"  Updated notes={user.notes!r}")
        by_email = await client.users.by_email(email)
        print(f"  by_email: id={by_email.id if by_email else None}")
        await client.users.delete(user.id)
        print(f"  Deleted user id={user.id}")
    except ZendeskHTTPException as exc:
        print(f"  Users CRUD skipped: {exc}")

    org_name = f"[SDK-ASYNC] Demo Org {stamp}"
    try:
        org = await client.organizations.create(
            org_name,
            details="Temporary org from api_usage_example",
            tags=[POC_TAG_SDK],
        )
        assert org.id is not None
        print(f"  Created org id={org.id} name={org.name}")
        org = await client.organizations.update(org.id, notes="Updated by api_usage_example")
        print(f"  Updated org notes={org.notes!r}")
        await client.organizations.delete(org.id)
        print(f"  Deleted org id={org.id}")
    except ZendeskHTTPException as exc:
        print(f"  Organizations CRUD skipped: {exc}")


async def demo_tags_and_enriched(
    client: ZendeskClient, *, interactive: bool, ticket_id: int, requester: User
) -> None:
    if not prompt_continue(
        "Tags + tickets list/get_many + enriched helpers",
        interactive=interactive,
        ticket_id=ticket_id,
    ):
        return

    current = await client.tickets.tags.get(ticket_id)
    print(f"  tags.get: {current}")
    tags = await client.tickets.tags.add(ticket_id, ["sdk_async_demo"])
    print(f"  Tags after add: {tags}")
    tags = await client.tickets.tags.set(ticket_id, list(dict.fromkeys([*tags, "sdk_set_demo"])))
    print(f"  Tags after set: {tags}")
    tags = await client.tickets.tags.remove(ticket_id, ["sdk_async_demo", "sdk_set_demo"])
    print(f"  Tags after remove demos: {tags}")

    last = await client.tickets.comments.get_last(ticket_id)
    if last:
        comment, author = last
        print(
            f"  comments.get_last: id={comment.id} "
            f"author={author.name if author else comment.author_id}"
        )

    listed = await client.tickets.list(limit=3).collect()
    print(f"  tickets.list sample: {len(listed)}")
    if requester.id:
        for_user = await client.tickets.for_user(requester.id, limit=3).collect()
        print(f"  tickets.for_user({requester.id}): {len(for_user)}")

    many = await client.tickets.get_many([ticket_id])
    print(f"  tickets.get_many: {list(many.keys())}")
    enriched = await client.tickets.get_enriched(ticket_id)
    print(
        f"  get_enriched: requester={enriched.requester.name if enriched.requester else None} "
        f"comments={len(enriched.comments)}"
    )
    many_enriched = await client.tickets.get_many_enriched([ticket_id])
    print(f"  get_many_enriched: {len(many_enriched)}")
    try:
        search_enriched = [
            e async for e in client.tickets.search_enriched(f"tags:{POC_TAG_SDK}", limit=3)
        ]
        print(f"  search_enriched: {len(search_enriched)}")
    except (ZendeskHTTPException, ZendeskPaginationException) as exc:
        print(f"  search_enriched skipped: {exc}")


async def run_example(*, interactive: bool, skip_close: bool) -> None:
    config = ZendeskConfig()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    created_ids: List[int] = []

    async with ZendeskClient(config) as client:
        print("=" * 70)
        print("ASYNC ZENDESK SDK — full API usage example (POC + checklist)")
        print(f"  Subdomain : {config.subdomain}")
        print(f"  Tag       : {POC_TAG_SDK}")
        print("  Note      : status transition rules are enforced by YOUR app, not the SDK")
        print("=" * 70)

        requester = await pick_requester(client, interactive)
        group, assignee = await pick_group_then_assignee(
            client,
            interactive,
            title="initial assignment (REQ-04/05)",
            preferred_group_id=ENV_GROUP_ID or None,
            preferred_assignee_id=ENV_ASSIGNEE_ID or None,
        )
        print(f"\nRequester : {requester.name} (id={requester.id})")
        print(f"Group     : {group.name} (id={group.id})")
        print(f"Assignee  : {assignee.name} (id={assignee.id}) — member of selected group")

        # Preload default brand for create (optional)
        brand_id: Optional[int] = None
        try:
            brands = await client.brands.list(limit=10).collect()
            chosen = next((b for b in brands if b.default and b.id), None) or (
                brands[0] if brands else None
            )
            brand_id = chosen.id if chosen else None
            if brand_id:
                print(f"Default brand_id for create: {brand_id}")
        except (ZendeskHTTPException, ZendeskPaginationException):
            pass

        # --- REQ-01 / REQ-15 / T01 / T04: create with real requester ---
        if not prompt_continue("Create ticket (REQ-01 / REQ-15)", interactive=interactive):
            raise SystemExit("Ticket creation is required.")

        custom_fields = opening_custom_fields()
        ticket = await client.tickets.create(
            comment_body=f"Async SDK example ticket. Requester: {requester.name}.",
            subject=f"[SDK-ASYNC] Zendesk POC parity ({stamp})",
            requester_id=requester.id,
            ticket_form_id=FORM_POC or None,
            brand_id=brand_id,
            tags=[POC_TAG, POC_TAG_SDK],
            custom_fields=custom_fields or None,
            public=True,
            priority="normal",
            ticket_type="question",
        )
        assert ticket.id is not None
        ticket_id = ticket.id
        created_ids.append(ticket_id)
        print(f"  Created ticket #{ticket_id} brand_id={ticket.brand_id}")
        print(f"  {ticket_url(config.subdomain, ticket_id)}")

        # T04 — auxiliary ticket with private first comment
        if prompt_continue("[T04] Create ticket with private first comment", interactive=interactive, ticket_id=ticket_id):
            aux = await client.tickets.create(
                comment_body="Private opening comment (T04).",
                subject=f"[SDK-ASYNC][T04] private first comment ({stamp})",
                requester_id=requester.id,
                tags=[POC_TAG_SDK, "t04"],
                public=False,
            )
            assert aux.id is not None
            created_ids.append(aux.id)
            print(f"  T04 auxiliary ticket #{aux.id} (first comment public={False})")

        # --- REQ-04 / REQ-05: assign group + agent ---
        if prompt_continue(
            f"Assign group={group.name} + agent={assignee.name} (REQ-04/05)",
            interactive=interactive,
            ticket_id=ticket_id,
        ):
            ticket = await client.tickets.update(
                ticket_id,
                group_id=group.id,
                assignee_id=assignee.id,
                comment={
                    "body": f"Assigned to {assignee.name} / {group.name}",
                    "public": False,
                },
            )
            print(f"  assignee_id={ticket.assignee_id} group_id={ticket.group_id}")
            if FORM_POC:
                ticket = await client.tickets.update(ticket_id, ticket_form_id=FORM_POC)
                print(f"  ticket_form_id={ticket.ticket_form_id}")

        # --- REQ-03 / REQ-08: public + internal comments ---
        for label, is_public in (
            ("1st public comment", True),
            ("2nd internal note", False),
            ("3rd public comment", True),
        ):
            if prompt_continue(f"Add comment: {label} (REQ-03/08)", interactive=interactive, ticket_id=ticket_id):
                await client.tickets.comments.add(ticket_id, f"[SDK-ASYNC] {label}", public=is_public)
                print(f"  Added ({'public' if is_public else 'internal'})")

        # make_private demo: add public then convert
        if prompt_continue("Make a public comment private", interactive=interactive, ticket_id=ticket_id):
            await client.tickets.comments.add(
                ticket_id, "[SDK-ASYNC] Will become private", public=True
            )
            comments = await client.tickets.comments.list(ticket_id).collect()
            last = comments[-1]
            if last.id:
                try:
                    await client.tickets.comments.make_private(ticket_id, last.id)
                    print(f"  Comment {last.id} made private")
                except ZendeskHTTPException as exc:
                    print(f"  make_private failed: {exc}")

        # --- A01 / A02: upload + attachment redact ---
        if prompt_continue("[A01/A02] Upload attachment and redact it", interactive=interactive, ticket_id=ticket_id):
            with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as tmp:
                tmp.write("Sensitive POC attachment content — redact me.\n")
                tmp_path = Path(tmp.name)
            try:
                token = await client.attachments.upload(
                    tmp_path.read_bytes(),
                    filename=tmp_path.name,
                    content_type="text/plain",
                )
                await client.tickets.comments.add(
                    ticket_id,
                    "[SDK-ASYNC] Comment with attachment (A01)",
                    public=False,
                    uploads=[token],
                )
                comments = await client.tickets.comments.list(ticket_id).collect()
                target = next((c for c in reversed(comments) if c.attachments), None)
                if target and target.id and target.attachments:
                    urls = [a.content_url for a in target.attachments if a.content_url]
                    if urls:
                        raw = await client.attachments.download(urls[0])
                        print(f"  attachments.download: {len(raw)} bytes")
                        await client.tickets.comments.redact_attachments(
                            ticket_id, target.id, urls
                        )
                        print(f"  Redacted {len(urls)} attachment URL(s) on comment {target.id}")
                    else:
                        print("  No content_url on attachments — skip redact")
                else:
                    print("  No attachment comment found — skip redact")
            finally:
                tmp_path.unlink(missing_ok=True)

        # --- C02: text redact ---
        if prompt_continue("[C02] Redact sensitive text in a comment", interactive=interactive, ticket_id=ticket_id):
            secret = "123.456.789-00"
            await client.tickets.comments.add(
                ticket_id,
                f"[SDK-ASYNC][C02] My CPF is {secret} (will redact).",
                public=False,
            )
            comments = await client.tickets.comments.list(ticket_id).collect()
            last = comments[-1]
            assert last.id is not None
            try:
                await client.tickets.comments.redact(ticket_id, last.id, secret)
                print(f"  Redacted text on comment {last.id}")
            except ZendeskHTTPException as exc:
                print(f"  Text redact via legacy endpoint failed ({exc}); trying html redact")
                html = (last.html_body or last.body or "").replace(
                    secret, f"<redact>{secret}</redact>"
                )
                await client.tickets.comments.redact_html(ticket_id, last.id, html)
                print(f"  HTML redact applied on comment {last.id}")

        # --- REQ-06 / REQ-07: transfer ---
        if prompt_continue(
            "Transfer to another group/agent (REQ-06/07) — optional",
            interactive=interactive,
            ticket_id=ticket_id,
        ):
            try:
                transfer_group, transfer_assignee = await pick_group_then_assignee(
                    client,
                    interactive,
                    title="transfer (REQ-06/07)",
                    preferred_group_id=ENV_TRANSFER_GROUP_ID or None,
                    preferred_assignee_id=ENV_TRANSFER_ASSIGNEE_ID or None,
                    exclude_group_id=None if interactive else group.id,
                    exclude_assignee_id=assignee.id,
                )
                ticket = await client.tickets.update(
                    ticket_id,
                    group_id=transfer_group.id,
                    assignee_id=transfer_assignee.id,
                    comment={
                        "body": (
                            f"Transferred to {transfer_assignee.name} / {transfer_group.name}"
                        ),
                        "public": False,
                    },
                )
                print(
                    f"  Transfer OK → group_id={ticket.group_id} "
                    f"assignee_id={ticket.assignee_id}"
                )
            except RuntimeError as exc:
                print(f"  Transfer skipped: {exc}")

        # --- REQ-02 / H01: history + audits ---
        if prompt_continue("Read full history: comments + audits (REQ-02 / H01)", interactive=interactive, ticket_id=ticket_id):
            comments = await client.tickets.comments.list(ticket_id).collect()
            for i, comment in enumerate(comments, 1):
                kind = "public" if comment.public else "internal"
                body = (comment.body or "")[:60]
                print(f"  {i}. [{kind}] {comment.created_at} — {body}")
            audits = await client.tickets.audits.list(ticket_id).collect()
            print(f"  Audits: {len(audits)}")
            filtered = client.tickets.audits.filter_events_by_type(audits, ["Change", "Comment"])
            print(f"  Audits with Change/Comment events (client filter): {len(filtered)}")

        # --- REQ-12 / F01 values ---
        if prompt_continue("Set/read POC custom fields (REQ-12 / F01)", interactive=interactive, ticket_id=ticket_id):
            if FIELD_PROPOSTA:
                await set_custom_field(client, ticket_id, FIELD_PROPOSTA, "POC-ASYNC-12345")
            ticket = await client.tickets.get(ticket_id)
            if FIELD_PROPOSTA:
                print(f"  Proposta = {field_value(ticket, FIELD_PROPOSTA)!r}")
            if FIELD_TIPO_CHAMADO:
                print(f"  Tipo = {field_value(ticket, FIELD_TIPO_CHAMADO)!r}")
            if FIELD_PRODUTO:
                print(f"  Produto = {field_value(ticket, FIELD_PRODUTO)!r}")
            if not (FIELD_PROPOSTA or FIELD_TIPO_CHAMADO or FIELD_PRODUTO):
                print("  No POC field IDs in .env — run POC setup or set ZENDESK_FIELD_*")

        await demo_ticket_fields_crud(client, interactive=interactive, ticket_id=ticket_id)

        # --- REQ-09 / 10 / 11 ---
        if FIELD_APROVACAO_SIMPLES and prompt_continue(
            "Simple approval (REQ-09)", interactive=interactive, ticket_id=ticket_id
        ):
            await set_custom_field(client, ticket_id, FIELD_APROVACAO_SIMPLES, "aprovado")
            await client.tickets.comments.add(
                ticket_id, "[SDK-ASYNC] Simple approval recorded.", public=False
            )
            print("  Simple approval = aprovado")

        if FIELD_APROVACAO_DUPLA and prompt_continue(
            "Dual approval (REQ-10)", interactive=interactive, ticket_id=ticket_id
        ):
            await set_custom_field(client, ticket_id, FIELD_APROVACAO_DUPLA, "manager_a")
            await client.tickets.comments.add(ticket_id, "manager_a approved", public=False)
            print("  Dual approval first approver recorded")

        if FIELD_APROVACAO_NIVEL and prompt_continue(
            "Level approval (REQ-11)", interactive=interactive, ticket_id=ticket_id
        ):
            for level in (1, 2, 3):
                await set_custom_field(
                    client, ticket_id, FIELD_APROVACAO_NIVEL, f"nivel_{level}_aprovado"
                )
                print(f"  Level {level} recorded")

        await demo_brands_and_ticket_params(
            client,
            interactive=interactive,
            ticket_id=ticket_id,
            requester=requester,
            created_ids=created_ids,
        )
        await demo_tags_and_enriched(
            client, interactive=interactive, ticket_id=ticket_id, requester=requester
        )
        await demo_users_and_orgs(client, interactive=interactive, ticket_id=ticket_id)
        await demo_admin_catalog(client, interactive=interactive, ticket_id=ticket_id)

        # --- O01: update_many ---
        if prompt_continue("[O01] Batch update auxiliary tickets", interactive=interactive, ticket_id=ticket_id):
            aux_ids: List[int] = []
            for i in range(2):
                aux = await client.tickets.create(
                    comment_body=f"Batch helper {i + 1}",
                    subject=f"[SDK-ASYNC][O01] batch helper {i + 1} ({stamp})",
                    requester_id=requester.id,
                    tags=[POC_TAG_SDK, "o01"],
                )
                assert aux.id is not None
                aux_ids.append(aux.id)
                created_ids.append(aux.id)
            job = await client.tickets.update_many(aux_ids, status="solved")
            assert job.id is not None
            done = await client.job_statuses.wait_until_done(job.id, timeout=90.0)
            print(f"  update_many job {done.id} -> {done.status}")
            # Soft-delete one auxiliary ticket (T06)
            deleted = await client.tickets.delete(aux_ids[0])
            print(f"  tickets.delete(#{aux_ids[0]}) -> {deleted}")

        # --- T05 ---
        if prompt_continue(
            "[T05] Sample status changes (caller decides allowed transitions)",
            interactive=interactive,
            ticket_id=ticket_id,
        ):
            for next_status in ("pending", "open"):
                try:
                    ticket = await client.tickets.update(ticket_id, status=next_status)
                    print(f"  status -> {ticket.status}")
                except ZendeskHTTPException as exc:
                    print(f"  status -> {next_status} rejected: {exc}")

        # --- T02 / REQ-01: close ---
        if not skip_close and prompt_continue(
            "[T02] Close ticket", interactive=interactive, ticket_id=ticket_id
        ):
            try:
                ticket = await client.tickets.update(ticket_id, status="closed")
                print(f"  Closed ticket #{ticket_id} (status={ticket.status})")
            except ZendeskHTTPException as exc:
                print(f"  Close failed: {exc}")
                print("  Tip: required form fields may block solved/closed on this account.")

            try:
                await client.tickets.comments.add(ticket_id, "Should fail on closed", public=False)
                print("  Unexpected: comment on closed ticket succeeded")
            except ZendeskHTTPException as exc:
                print(f"  Expected: cannot comment on closed ticket ({exc.status_code})")

        print("\n" + "=" * 70)
        print(f"Done. Primary ticket: #{ticket_id}")
        print(f"  {ticket_url(config.subdomain, ticket_id)}")
        print(f"  Tickets touched this run: {created_ids}")
        print("=" * 70)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Async Zendesk SDK POC-parity example")
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Pause before each step (Enter/s/q), like poc_zendesk.py",
    )
    parser.add_argument(
        "--skip-close",
        action="store_true",
        help="Do not close the primary ticket at the end",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv)
    if not os.getenv("ZENDESK_SUBDOMAIN") or not os.getenv("ZENDESK_EMAIL") or not os.getenv("ZENDESK_TOKEN"):
        print(
            "Missing ZENDESK_SUBDOMAIN / ZENDESK_EMAIL / ZENDESK_TOKEN.\n"
            f"Copy {ROOT / '.env.example'} to {ROOT / '.env'} and fill values.",
            file=sys.stderr,
        )
        raise SystemExit(1)
    asyncio.run(run_example(interactive=args.interactive, skip_close=args.skip_close))


if __name__ == "__main__":
    main()
