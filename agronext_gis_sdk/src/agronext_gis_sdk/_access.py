"""Who the caller is, and — for an admin — the users, their keys and the audit trail."""

import datetime
import uuid
from typing import Any

from agronext_gis_sdk._http import API_PREFIX, HttpClient
from agronext_gis_sdk._wire import Page, WireModel

_ACCESS = f"{API_PREFIX}/access"


class CurrentUserResponse(WireModel):
    """The caller behind the key. `can_write` is the whole of authorization."""

    id: int
    username: str
    display_name: str | None
    can_write: bool
    is_admin: bool


class SecretResponse(WireModel):
    """A credential, shown exactly once: losing this answer means minting another."""

    password: str | None = None
    api_key: str | None = None


class UserListItem(WireModel):
    id: int
    username: str
    display_name: str | None
    is_admin: bool
    can_write: bool
    is_active: bool
    #: False for a calling system, which signs nothing in and uses its key.
    has_password: bool
    live_key_count: int
    created_at: datetime.datetime


class CreateUserRequest(WireModel):
    """`with_password=False` creates a CALLING SYSTEM: no password, a key only."""

    username: str
    display_name: str | None = None
    is_admin: bool = False
    can_write: bool = False
    with_password: bool = True


class CreatedUserResponse(WireModel):
    id: int
    username: str
    secret: SecretResponse


class UpdateAccessRequest(WireModel):
    """All three flags, always together."""

    is_admin: bool
    can_write: bool
    is_active: bool


class ChangeLogItem(WireModel):
    """One entry of the audit trail. `before`/`after` carry the fields that moved."""

    id: int
    entity: str
    entity_id: str
    operation: str
    before: dict[str, Any] | None
    after: dict[str, Any] | None
    note: str | None
    occurred_at: datetime.datetime
    actor_username: str
    correlation_id: uuid.UUID


class Access:
    """`gis.access` — the caller, and the admin's user management."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def me(self) -> CurrentUserResponse:
        """The user behind this client's key."""
        return await self._http.model(CurrentUserResponse, "GET", f"{_ACCESS}/me")

    async def rotate_my_key(self) -> SecretResponse:
        """Replace this client's own key. The new one is in the answer, once."""
        return await self._http.model(SecretResponse, "POST", f"{_ACCESS}/me/key")

    async def list_users(self, *, page: int = 1, size: int | None = None) -> Page[UserListItem]:
        """Everyone, a page at a time. Admin only."""
        return await self._http.model(
            Page[UserListItem], "GET", f"{_ACCESS}/users", query={"page": page, "size": size}
        )

    async def create_user(self, request: CreateUserRequest) -> CreatedUserResponse:
        """A person or a calling system. Its password, if any, is in the answer, once."""
        return await self._http.model(CreatedUserResponse, "POST", f"{_ACCESS}/users", body=request)

    async def set_user_access(self, user_id: int, request: UpdateAccessRequest) -> None:
        """Set all three flags. Deactivating ends the user's live sessions."""
        await self._http.nothing("PUT", f"{_ACCESS}/users/{user_id}/access", body=request)

    async def reset_password(self, user_id: int) -> SecretResponse:
        """A new password, shown once. The user's live sessions end with it."""
        return await self._http.model(SecretResponse, "POST", f"{_ACCESS}/users/{user_id}/password")

    async def rotate_user_key(self, user_id: int) -> SecretResponse:
        """Revoke the user's live key and mint a replacement, shown once."""
        return await self._http.model(SecretResponse, "POST", f"{_ACCESS}/users/{user_id}/key")

    async def list_changes(
        self,
        *,
        entity: str | None = None,
        entity_id: str | None = None,
        actor_user_id: int | None = None,
        page: int = 1,
        size: int | None = None,
    ) -> Page[ChangeLogItem]:
        """Who changed what, when — newest first. Admin only."""
        return await self._http.model(
            Page[ChangeLogItem],
            "GET",
            f"{_ACCESS}/changes",
            query={
                "entity": entity,
                "entityId": entity_id,
                "actorUserId": actor_user_id,
                "page": page,
                "size": size,
            },
        )


__all__ = [
    "Access",
    "ChangeLogItem",
    "CreateUserRequest",
    "CreatedUserResponse",
    "CurrentUserResponse",
    "SecretResponse",
    "UpdateAccessRequest",
    "UserListItem",
]
