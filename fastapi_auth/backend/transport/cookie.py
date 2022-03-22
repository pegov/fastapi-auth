from typing import Optional

from fastapi import Request, Response

from fastapi_auth.backend.abc.transport import AbstractTransport


class CookieTransport(AbstractTransport):
    def __init__(
        self,
        access_cookie_name: str,
        refresh_cookie_name: str,
        secure: bool = True,
    ):
        self._access_cookie_name = access_cookie_name
        self._refresh_cookie_name = refresh_cookie_name
        self._secure = secure

    def _set_access_token_cookie(
        self,
        response: Response,
        token: str,
        expiration: int,
    ) -> None:
        response.set_cookie(
            key=self._access_cookie_name,
            value=token,
            expires=expiration,
            secure=self._secure,
            httponly=True,
        )

    def _set_refresh_token_cookie(
        self,
        response: Response,
        token: str,
        expiration: int,
    ) -> None:
        response.set_cookie(
            key=self._refresh_cookie_name,
            value=token,
            expires=expiration,
            secure=self._secure,
            httponly=True,
        )

    def login(
        self,
        response: Response,
        access_token: str,
        refresh_token: str,
        access_token_expiration: int,
        refresh_token_expiration: int,
    ) -> None:
        self._set_access_token_cookie(
            response,
            access_token,
            access_token_expiration,
        )
        self._set_refresh_token_cookie(
            response,
            refresh_token,
            refresh_token_expiration,
        )

    def logout(self, response: Response) -> None:
        response.delete_cookie(self._access_cookie_name)
        response.delete_cookie(self._refresh_cookie_name)

    def refresh_access_token(self, response, token: str, expiration: int) -> None:
        self._set_access_token_cookie(response, token, expiration)

    def get_access_token(self, request: Request) -> Optional[str]:
        return request.cookies.get(self._access_cookie_name)

    def get_refresh_token(self, request: Request) -> Optional[str]:
        return request.cookies.get(self._refresh_cookie_name)
