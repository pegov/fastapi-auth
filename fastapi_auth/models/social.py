from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, validator


def set_created_at(v):
    return datetime.utcnow()


def set_last_login(v, values):
    return values.get("created_at")


class SocialInCreate(BaseModel):
    email: EmailStr
    username: str
    provider: str
    sid: str
    active: bool = True
    confirmed: bool = True
    permissions: list = []
    info: list = []
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    _created_at = validator("created_at", pre=True, always=True, allow_reuse=True)(
        set_created_at
    )
    _last_login = validator("last_login", pre=True, always=True, allow_reuse=True)(
        set_last_login
    )
