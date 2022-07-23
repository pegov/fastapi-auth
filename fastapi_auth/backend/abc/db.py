from abc import ABC, abstractmethod
from typing import List, Optional

from fastapi_auth.models.user import OAuthDB, RoleDB, UserCreate, UserDB


class AbstractDatabaseOAuthExtension(ABC):
    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> Optional[OAuthDB]:
        raise NotImplementedError

    @abstractmethod
    async def create(self, user_id: int, provider: str, sid: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_by_user_id(self, user_id: int, provider: str, sid: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete_by_user_id(self, user_id: int) -> None:
        raise NotImplementedError


class AbstractDatabaseRolesExtension(ABC):
    @abstractmethod
    async def create(self, name: str) -> int:
        raise NotImplementedError

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[RoleDB]:
        raise NotImplementedError

    @abstractmethod
    async def add_permission(self, role_name: str, permission_name: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def remove_permission(self, role_name: str, permission_name: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete_by_name(self, name: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def grant(self, user_id: int, role_name: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def revoke(self, user_id: int, role_name: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def all(self) -> List[RoleDB]:
        raise NotImplementedError


class AbstractDatabaseClient(ABC):
    oauth: AbstractDatabaseOAuthExtension
    roles: AbstractDatabaseRolesExtension

    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[UserDB]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[UserDB]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[UserDB]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_provider_and_sid(
        self,
        provider: str,
        sid: str,
    ) -> Optional[UserDB]:
        raise NotImplementedError

    @abstractmethod
    async def create(self, obj: UserCreate) -> int:
        raise NotImplementedError

    @abstractmethod
    async def update_by_id(self, id: int, obj: dict) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def delete_by_id(self, id: int) -> bool:
        raise NotImplementedError
