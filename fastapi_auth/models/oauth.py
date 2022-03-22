from pydantic import BaseModel

from fastapi_auth.types import UID


class OAuthAccountActionToken(BaseModel):
    id: UID
    type: str
