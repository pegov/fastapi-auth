from typing import List

from pydantic import BaseModel

from fastapi_auth.types import UID


class TokenPayloadResponse(BaseModel):
    id: UID
    username: str
    roles: List[str]


class RefreshAccessTokenResponse(BaseModel):
    access_token: str
