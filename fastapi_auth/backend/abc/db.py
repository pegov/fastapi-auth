from abc import ABC, abstractmethod

from fastapi_auth.models.user import UserDB
from fastapi_auth.types import UID


class AbstractDatabaseClient(ABC):
    @abstractmethod
    async def get(self, id: UID) -> UserDB:
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: str) -> UserDB:
        raise NotImplementedError

    @abstractmethod
    async def get_by_username(self, username: str) -> UserDB:
        raise NotImplementedError

    @abstractmethod
    async def get_by_oauth(self, provider: str, sid: str) -> UserDB:
        raise NotImplementedError

    @abstractmethod
    async def create(self, obj: dict) -> UID:
        raise NotImplementedError

    @abstractmethod
    async def update(self, id: UID, obj: dict) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, id: UID) -> bool:
        raise NotImplementedError
