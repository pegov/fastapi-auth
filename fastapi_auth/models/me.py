from typing import List, Optional

from pydantic import BaseModel, validator

from fastapi_auth.models.user import OAuthDB
from fastapi_auth.validator import GlobalValidator


class MeResponse(BaseModel):
    id: int
    email: str
    username: str
    roles: List[str]

    oauth: Optional[OAuthDB]

    verified: bool


class ChangeUsernameRequest(BaseModel):
    username: str

    _check_username = validator("username", allow_reuse=True)(
        GlobalValidator._validator.validate_username
    )
