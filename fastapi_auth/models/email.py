from pydantic import BaseModel, EmailStr

from fastapi_auth.types import UID


class ChangeEmailRequest(BaseModel):
    email: EmailStr


class EmailActionTokenPayload(BaseModel):
    id: UID
    email: str

    type: str
