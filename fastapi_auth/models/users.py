from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, validator

from fastapi_auth.models.common import DefaultModel
from fastapi_auth.validator import Validator


class Me(DefaultModel):
    id: int
    email: str
    username: str

    provider: Optional[str] = None

    active: bool
    verified: bool

    roles: List[str]

    created_at: datetime
    last_login: datetime


class UpdateMe(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None

    @validator("username")
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return Validator._validator.validate_username(v)
