from abc import ABC, abstractmethod
from typing import Iterable, Optional, Tuple, Union

from fastapi import Request, Response

from fastapi_auth.user import User


class AbstractJWTAuthentication(ABC):
    @abstractmethod
    def create_access_token(self, payload: dict) -> str:
        raise NotImplementedError

    @abstractmethod
    def create_refresh_token(self, payload: dict) -> str:
        raise NotImplementedError

    def create_tokens(self, payload: dict) -> Tuple[str, str]:
        return self.create_access_token(payload), self.create_refresh_token(payload)

    @abstractmethod
    def get_access_token_from_request(self, request: Request) -> Optional[str]:
        raise NotImplementedError

    @abstractmethod
    def get_refresh_token_from_request(self, request: Request) -> Optional[str]:
        raise NotImplementedError

    @abstractmethod
    def decode_token(self, token: str, leeway: int = 0) -> Optional[dict]:
        raise NotImplementedError

    @abstractmethod
    async def token_is_valid(self, id: int, iat: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        raise NotImplementedError

    @abstractmethod
    def set_access_cookie(self, response: Response, value: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_login_response(
        self, response: Response, access_token: str, refresh_token: str
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_logout_response(self, response: Response) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_user(self, request: Request) -> Optional[User]:
        raise NotImplementedError


class AbstractCacheBackend(ABC):
    @abstractmethod
    async def get(self, key: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, key: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def keys(self, match: str) -> Iterable[str]:
        raise NotImplementedError

    @abstractmethod
    async def set(self, key: str, value: Union[str, bytes, int], ex: int = 0) -> None:
        raise NotImplementedError

    @abstractmethod
    async def setnx(self, key: str, value: Union[str, bytes, int], ex: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def incr(self, key: str) -> int:
        raise NotImplementedError


class AbstractCaptchaBackend(ABC):
    @abstractmethod
    async def validate_captcha(self, captcha: Optional[str]) -> bool:
        raise NotImplementedError


class AbstractDBBackend(ABC):
    @abstractmethod
    async def get(self, id: int) -> Optional[dict]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[dict]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[dict]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_social(self, provider: str, sid: str) -> Optional[dict]:
        raise NotImplementedError

    @abstractmethod
    async def create(self, obj: dict) -> int:
        """Create user, return id."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, id: int, obj: dict) -> bool:
        """Update user data, return True if success."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, id: int) -> bool:
        """Delete user, return True if success."""
        raise NotImplementedError

    @abstractmethod
    async def request_verification(self, email: str, token_hash: str) -> None:
        """Create email confirmation"""
        raise NotImplementedError

    @abstractmethod
    async def verify(self, token_hash: str) -> bool:
        """If success, return True."""
        raise NotImplementedError

    @abstractmethod
    async def get_blacklist(self) -> Iterable[dict]:
        raise NotImplementedError

    @abstractmethod
    async def search(
        self,
        id: Optional[int],
        username: Optional[str],
        p: int,
        size: int,
    ) -> Tuple[dict, int]:
        raise NotImplementedError


class AbstractEmailBackend(ABC):
    @abstractmethod
    async def request_verification(self, email: str, token: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def request_password_reset(self, email: str, token: str) -> None:
        raise NotImplementedError


class AbstractOAuthProvider:
    name: str

    def __init__(self, id: str, secret: str) -> None:
        self._id = id
        self._secret = secret

    @abstractmethod
    def create_oauth_uri(self, redirect_uri: str, state: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def get_user_data(self, redirect_uri: str, code: str) -> Tuple[str, str]:
        """Return sid and email."""
        raise NotImplementedError


class AbstractUserValidator(ABC):
    @abstractmethod
    def validate_username(self, v: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def validate_password(self, v: str, values) -> str:
        raise NotImplementedError
