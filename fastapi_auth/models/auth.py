from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, EmailStr, validator

from fastapi_auth.models.common import set_created_at, set_last_login
from fastapi_auth.validator import Validator


class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password1: str
    password2: str
    captcha: Optional[str]

    _check_username = validator("username", allow_reuse=True)(
        Validator._validator.validate_username
    )
    _check_password = validator("password2", allow_reuse=True)(
        Validator._validator.validate_password
    )


class UserLogin(BaseModel):
    login: Union[EmailStr, str]
    password: str


class BaseUserTokenPayload(BaseModel):
    id: int


class UserTokenPayload(BaseUserTokenPayload):
    id: int
    username: str
    roles: List[str] = []


class BaseUserCreate(BaseModel):
    email: str
    username: str
    password: str


class UserCreate(BaseUserCreate):
    # email: str
    # username: str
    # password: str
    active: bool = True
    confirmed: bool = False
    roles: List[str] = []

    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    _created_at = validator("created_at", pre=True, always=True, allow_reuse=True)(
        set_created_at
    )
    _last_login = validator("last_login", pre=True, always=True, allow_reuse=True)(
        set_last_login
    )


class UserTokenRefreshResponse(BaseModel):
    access_token: str


class UserEmailConfirmationStatusResponse(BaseModel):
    email: str
    confirmed: bool


class UserChangeUsername(BaseModel):
    username: str

    _check_username = validator("username")(Validator._validator.validate_username)
