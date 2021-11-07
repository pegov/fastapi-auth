from pydantic import BaseModel


class Status(BaseModel):
    email: str
    verified: bool
