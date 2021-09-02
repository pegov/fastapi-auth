from typing import Optional

from pydantic import validator

from fastapi_auth.models.common import DefaultModel
from fastapi_auth.validator import Validator


class PasswordForgot(DefaultModel):
    email: str
    captcha: Optional[str] = None


class PasswordSet(DefaultModel):
    password1: str
    password2: str

    _check_password2 = validator("password2")(Validator._validator.validate_password)


class PasswordHasPasswordResponse(DefaultModel):
    has_password: bool


class PasswordChange(PasswordSet):
    old_password: str


class PasswordReset(PasswordChange):
    pass
