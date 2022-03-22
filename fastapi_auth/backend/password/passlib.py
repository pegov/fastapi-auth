from typing import List

from passlib.context import CryptContext

from fastapi_auth.backend.abc.password import AbstractPasswordBackend


class PasslibPasswordBackend(AbstractPasswordBackend):
    def __init__(self, schemes: List[str] = ["bcrypt"]) -> None:
        self.pwd_context = CryptContext(
            schemes=schemes,
            deprecated="auto",
        )

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def hash(self, password: str) -> str:
        return self.pwd_context.hash(password)
