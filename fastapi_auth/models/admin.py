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


# TODO: custom
class AdminUser(DefaultModel):
    id: int
    email: str
    username: str
    provider: Optional[str]
    sid: Optional[str]
    active: bool
    confirmed: bool
