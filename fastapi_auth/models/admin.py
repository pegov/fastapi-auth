from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from .common import DefaultModel


class BlacklistItem(BaseModel):
    id: int
    username: str


class Blacklist(BaseModel):
    all: List[BlacklistItem]
    recent: List[BlacklistItem]


class Blackout(BaseModel):
    ts: int


class UserInfo(DefaultModel):
    id: int
    email: str
    username: str
    provider: Optional[str] = None
    active: bool
    verified: bool

    created_at: datetime
    last_login: datetime


class UpdateUser(DefaultModel):
    email: Optional[str] = None
    username: Optional[str] = None
    active: Optional[bool] = None  # TODO
    verified: Optional[bool] = None
