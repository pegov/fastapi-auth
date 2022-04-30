from pydantic import BaseModel

from fastapi_auth.types import UID


class OAuthAccountActionTokenPayload(BaseModel):
    id: UID
    type: str
