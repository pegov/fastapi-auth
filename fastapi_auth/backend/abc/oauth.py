from abc import ABC, abstractmethod
from typing import Tuple


class AbstractOAuthProvider(ABC):
    name: str

    @abstractmethod
    def create_oauth_uri(self, redirect_uri: str, state: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def get_user_data(self, redirect_uri: str, code: str) -> Tuple[str, str]:
        """Return sid and email."""
        raise NotImplementedError

    @abstractmethod
    def is_login_only(self) -> bool:
        raise NotImplementedError
