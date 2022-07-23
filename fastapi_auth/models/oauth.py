from pydantic import BaseModel


class OAuthAccountActionTokenPayload(BaseModel):
    id: int
    type: str
