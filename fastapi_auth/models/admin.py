from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class BlacklistItem(BaseModel):
    id: int
    username: str


class Blacklist(BaseModel):
    all: List[BlacklistItem]
    recent: List[BlacklistItem]


class Blackout(BaseModel):
    active: bool
    date: Optional[datetime] = None
