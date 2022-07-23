from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, validator

from fastapi_auth.models.common import DefaultModel


def set_created_at(v):
    if v is None:
        return datetime.now(timezone.utc)

    return v


def set_last_login(v, values):
    if v is None:
        return values.get("created_at")

    return v


class ToPayload(BaseModel):
    id: int
    username: str
    roles: List[str]
    permissions: List[str]

    def payload(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "roles": self.roles,
            "permissions": self.permissions,
        }


class OAuthDB(DefaultModel):
    user_id: int
    provider: str
    sid: str


class UserDB(DefaultModel, ToPayload):
    id: int

    email: str
    username: str
    password: Optional[str]

    roles: List[str]
    permissions: List[str]

    active: bool
    verified: bool

    created_at: datetime
    last_login: datetime

    oauth: Optional[OAuthDB]


class UserCreate(DefaultModel):
    email: str
    username: str
    password: Optional[str] = None

    active: bool = True
    verified: bool = False

    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    _created_at = validator("created_at", pre=True, always=True, allow_reuse=True)(
        set_created_at
    )
    _last_login = validator("last_login", pre=True, always=True, allow_reuse=True)(
        set_last_login
    )


class User(ToPayload):
    id: int
    username: str
    roles: List[str]
    permissions: Optional[List[str]] = None  # for backward compatability

    iat: int
    exp: int
    type: str

    def is_authenticated(self) -> bool:
        return True

    def has_role(self, role: str) -> bool:
        return role in self.roles

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions

    def is_admin(self) -> bool:
        return self.has_role("admin")


class UserUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

    roles: Optional[List[str]] = None

    active: Optional[bool] = None
    verified: Optional[bool] = None

    last_login: Optional[datetime] = None

    def to_update_dict(self) -> dict:
        return self.dict(
            exclude_none=True,
            by_alias=True,
        )


class RoleDB(BaseModel):
    id: int
    name: str
    permissions: List[str]
