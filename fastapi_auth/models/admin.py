from typing import List

from pydantic import BaseModel


class BlacklistItem(BaseModel):
    id: int
    username: str


class Blacklist(BaseModel):
    all: List[BlacklistItem]
    recent: List[BlacklistItem]


class Blackout(BaseModel):
    ts: int
