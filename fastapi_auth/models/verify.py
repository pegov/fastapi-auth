from pydantic import BaseModel

from fastapi_auth.types import UID


class VerificationStatusResponse(BaseModel):
    email: str
    verified: bool


class VerificationPayload(BaseModel):
    id: UID
    email: str
    type: str
