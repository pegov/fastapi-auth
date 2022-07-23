from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class RoleCreate(BaseModel):
    name: str


class RoleUpdate(BaseModel):
    add: Optional[str] = None
    remove: Optional[str] = None


class MassLogoutStatusResponse(BaseModel):
    active: bool
    date: Optional[datetime] = None
