from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from .common import DefaultModel


class AdminBlacklistItem(BaseModel):
    id: int
    username: str


class AdminBlacklist(BaseModel):
    all: List[AdminBlacklistItem]
    recent: List[AdminBlacklistItem]


class AdminBlackout(BaseModel):
    ts: int


class AdminUser(DefaultModel):
    id: int
    email: str
    username: str
    provider: Optional[str] = None
    active: bool
    verified: bool

    created_at: datetime
    last_login: datetime


class AdminUpdateUser(DefaultModel):
    email: Optional[str] = None
    username: Optional[str] = None
    verified: Optional[bool] = None
