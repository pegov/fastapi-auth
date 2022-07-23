from typing import List

from pydantic import BaseModel


class TokenPayloadResponse(BaseModel):
    id: int
    username: str
    roles: List[str]


class RefreshAccessTokenResponse(BaseModel):
    access_token: str
