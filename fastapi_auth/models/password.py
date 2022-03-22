from typing import Optional

from pydantic import BaseModel, validator

from fastapi_auth.models.common import DefaultModel
from fastapi_auth.types import UID
from fastapi_auth.validator import GlobalValidator


class PasswordForgotRequest(BaseModel):
    email: str
    captcha: Optional[str] = None


class PasswordSetRequest(DefaultModel):
    password1: str
    password2: str

    _check_password2 = validator("password2")(
        GlobalValidator._validator.validate_password
    )


class PasswordChangeRequest(PasswordSetRequest):
    old_password: str


class PasswordStatusResponse(DefaultModel):
    has_password: bool


class PasswordResetRequest(PasswordSetRequest):
    token: str


class PasswordResetToken(BaseModel):
    id: UID
    type: str
