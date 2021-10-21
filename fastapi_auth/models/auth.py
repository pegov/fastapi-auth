from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, EmailStr, validator

from fastapi_auth.models.common import DefaultModel, set_created_at, set_last_login
from fastapi_auth.validator import Validator


class Register(BaseModel):
    email: EmailStr
    username: str
    password1: str
    password2: str
    captcha: Optional[str] = None

    _check_username = validator("username", allow_reuse=True)(
        Validator._validator.validate_username
    )
    _check_password = validator("password2", allow_reuse=True)(
        Validator._validator.validate_password
    )


class Login(BaseModel):
    login: Union[EmailStr, str]
    password: str


class BaseTokenPayload(BaseModel):
    id: int


class TokenPayload(BaseTokenPayload):
    id: int
    username: str
    roles: List[str] = []


class Create(BaseModel):
    email: str
    username: str
    password: str
    active: bool = True
    verified: bool = False
    roles: List[str] = []

    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    _created_at = validator("created_at", pre=True, always=True, allow_reuse=True)(
        set_created_at
    )
    _last_login = validator("last_login", pre=True, always=True, allow_reuse=True)(
        set_last_login
    )


class TokenRefreshResponse(BaseModel):
    access_token: str


# NOTE: already exists in account
# TODO: remove
class VerificationStatusResponse(BaseModel):
    email: str
    verified: bool


class ChangeUsername(BaseModel):
    username: str

    _check_username = validator("username", allow_reuse=True)(
        Validator._validator.validate_username
    )


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
