from datetime import datetime, timedelta
from string import ascii_letters
from typing import List, Optional, Union

from pydantic import BaseModel, EmailStr, validator

from fastapi_auth.core.config import (
    MAX_PASSWORD_LENGTH,
    MAX_USERNAME_LENGTH,
    MIN_PASSWORD_LENGTH,
    MIN_USERNAME_LENGTH,
    PASSWORD_CHARS,
    TIME_DELTA,
    USERNAME_CHARS,
    WRONG_USERNAMES,
    russian_letters,
)
from fastapi_auth.models.common import DefaultModel


def check_username(v: str) -> str:
    v = v.strip()
    if not len(v) >= MIN_USERNAME_LENGTH or not len(v) <= MAX_USERNAME_LENGTH:
        raise ValueError("username length")
    for letter in v:
        if letter not in USERNAME_CHARS:
            raise ValueError("username special characters")
    if v in WRONG_USERNAMES:
        raise ValueError("username wrong")
    if any(letter in ascii_letters for letter in v):
        if any(letter in russian_letters for letter in v):
            raise ValueError("username different letters")
    if any(letter in russian_letters for letter in v):
        if any(letter in ascii_letters for letter in v):
            raise ValueError("username different letters")

    return v


def check_password(v: str, values) -> str:
    if " " in v:
        raise ValueError("password space")
    if not len(v) >= MIN_PASSWORD_LENGTH or not len(v) <= MAX_PASSWORD_LENGTH:
        raise ValueError("password length")
    if v != values.get("password1"):
        raise ValueError("password mismatch")
    for letter in v:
        if letter not in PASSWORD_CHARS:
            raise ValueError("password special")

    return v


def set_created_at(v):
    return datetime.utcnow()


def set_last_login(v, values):
    return values.get("created_at")


class UserInRegister(BaseModel):
    email: EmailStr
    username: str
    password1: str
    password2: str

    _check_username = validator("username", allow_reuse=True)(check_username)

    _check_password2 = validator("password2", allow_reuse=True)(check_password)


class UserInCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    active: bool = True
    confirmed: bool = False
    permissions: List[str] = []
    info: list = []
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    _created_at = validator("created_at", pre=True, always=True, allow_reuse=True)(
        set_created_at
    )
    _last_login = validator("last_login", pre=True, always=True, allow_reuse=True)(
        set_last_login
    )


class UserInLogin(BaseModel):
    login: Union[EmailStr, str]
    password: str


class UserInForgotPassword(BaseModel):
    email: EmailStr


class UserPayload(BaseModel):
    id: int
    username: str
    permissions: List[str] = []


class UserInSetPassword(DefaultModel):
    password1: str
    password2: str

    _check_password = validator("password2", allow_reuse=True)(check_password)


class UserInChangePassword(UserInSetPassword):
    old_password: str

    @validator("old_password")
    def check_old_password(cls, v, values):
        if v == values.get("password1"):
            raise ValueError("password same")
        return v


class UserInChangeUsername(DefaultModel):
    username: str

    _check_username = validator("username", allow_reuse=True)(check_username)


class UserPrivateInfo(DefaultModel):
    id: int
    username: str
    email: str
    active: bool
    sid: Optional[str] = None
    provider: Optional[str] = None
    confirmed: bool
    created_at: datetime
    last_login: datetime

    @validator("created_at", "last_login")
    def set_format(cls, v):
        d = v + timedelta(hours=TIME_DELTA)
        return d.strftime("%-d %B %Y, %H:%M")
