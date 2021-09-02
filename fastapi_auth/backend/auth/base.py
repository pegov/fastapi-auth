from typing import Optional, Tuple

from fastapi import Request, Response

from fastapi_auth.user import User


class BaseJWTAuthentication:
    def create_access_token(self, payload: dict) -> str:
        raise NotImplementedError

    def create_refresh_token(self, payload: dict) -> str:
        raise NotImplementedError

    def create_tokens(self, payload: dict) -> Tuple[str, str]:
        return self.create_access_token(payload), self.create_refresh_token(payload)

    def get_access_token_from_request(self, request: Request) -> Optional[str]:
        raise NotImplementedError

    def get_refresh_token_from_request(self, request: Request) -> Optional[str]:
        raise NotImplementedError

    def decode_token(self, token: str, leeway: int = 0) -> Optional[dict]:
        raise NotImplementedError

    async def token_is_valid(self, id: int, iat: int) -> bool:
        raise NotImplementedError

    async def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        raise NotImplementedError

    def set_access_cookie(self, response: Response, value: str) -> None:
        raise NotImplementedError

    def set_login_response(
        self, response: Response, access_token: str, refresh_token: str
    ) -> None:
        raise NotImplementedError

    def set_logout_response(self, response: Response) -> None:
        raise NotImplementedError

    async def get_user(self, request: Request) -> Optional[User]:
        raise NotImplementedError
