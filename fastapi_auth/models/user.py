from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, validator

from fastapi_auth.models.common import DefaultModel
from fastapi_auth.types import UID


def set_created_at(v):
    if v is None:
        return datetime.now(timezone.utc)

    return v


def set_last_login(v, values):
    if v is None:
        return values.get("created_at")

    return v


class ToPayload(BaseModel):
    id: UID
    username: str
    roles: List[str]

    def payload(self) -> dict:
        return {
            "id": str(self.id) if isinstance(self.id, UUID) else self.id,
            "username": self.username,
            "roles": self.roles,
        }


class OAuth(DefaultModel):
    provider: str
    sid: str


class UserDB(DefaultModel, ToPayload):
    id: UID

    email: str
    username: str
    password: Optional[str]

    roles: List[str]

    oauth: Optional[OAuth]

    active: bool
    verified: bool

    created_at: datetime
    last_login: datetime


class UserCreate(DefaultModel):
    email: str
    username: str
    password: Optional[str] = None

    roles: List[str] = []

    oauth: Optional[OAuth] = None

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


class BaseUser:
    id: UID
    username: str
    roles: List[str]

    iat: int
    exp: int
    type: str

    def is_authenticated(self) -> bool:
        raise NotImplementedError

    def has_role(self, role: str) -> bool:
        raise NotImplementedError

    def is_admin(self) -> bool:
        raise NotImplementedError

    def payload(self) -> dict:
        raise NotImplementedError


class Anonim(BaseUser):
    def is_authenticated(self) -> bool:
        return False

    def has_role(self, role: str) -> bool:
        return False

    def is_admin(self) -> bool:
        return False

    def payload(self) -> dict:
        return {}


class User(ToPayload, BaseUser):
    id: UID
    username: str
    roles: List[str]

    iat: int
    exp: int
    type: str

    def is_authenticated(self) -> bool:
        return True

    def has_role(self, role: str) -> bool:
        return role in self.roles

    def is_admin(self) -> bool:
        return self.has_role("admin")


class UserUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

    roles: Optional[List[str]] = None

    oauth: Optional[OAuth] = None

    active: Optional[bool] = None
    verified: Optional[bool] = None

    last_login: Optional[datetime] = None

    def to_update_dict(self) -> dict:
        return self.dict(
            exclude_none=True,
            by_alias=True,
        )

    def remove_oauth_account(self) -> dict:
        return {"oauth": None}
