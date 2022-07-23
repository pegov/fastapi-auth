from pydantic import BaseModel, EmailStr


class ChangeEmailRequest(BaseModel):
    email: EmailStr


class EmailActionTokenPayload(BaseModel):
    id: int
    email: str

    type: str
