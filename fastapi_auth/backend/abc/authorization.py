from abc import ABC, abstractmethod

from fastapi_auth.models.user import User
from fastapi_auth.repo import Repo


class AbstractAuthorization(ABC):
    @abstractmethod
    async def authorize(self, repo: Repo, user: User, token_type: str) -> None:
        raise NotImplementedError
