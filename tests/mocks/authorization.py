from fastapi_auth.backend.abc.authorization import AbstractAuthorization
from fastapi_auth.models.user import User
from fastapi_auth.repo import Repo


class MockAuthorization(AbstractAuthorization):
    async def authorize(self, repo: Repo, user: User, token_type: str) -> None:
        pass
