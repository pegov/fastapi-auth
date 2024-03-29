from typing import Optional

from pydantic import BaseModel, EmailStr, validator

from fastapi_auth.validator import GlobalValidator


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password1: str
    password2: str
    captcha: Optional[str] = None

    _check_username = validator("username", allow_reuse=True)(
        GlobalValidator._validator.validate_username
    )
    _check_password = validator("password2", allow_reuse=True)(
        GlobalValidator._validator.validate_password
    )


class LoginRequest(BaseModel):
    login: str
    password: str
