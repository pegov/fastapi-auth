import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import jwt
from fastapi import Request, Response

from fastapi_auth.backend.abc import AbstractJWTAuthentication
from fastapi_auth.models.auth import TokenPayload
from fastapi_auth.repo import AuthRepo
from fastapi_auth.user import User


class JWTCookieAuthentication(AbstractJWTAuthentication):
    def __init__(
        self,
        repo: AuthRepo,
        debug: bool = False,
        algorithm: str = "RS256",
        private_key: Any = "",
        public_key: Any = "",
        access_token_cookie_name: str = "access",
        access_token_expiration: int = 60 * 60 * 6,
        refresh_token_cookie_name: str = "refresh",
        refresh_token_expiration: int = 60 * 60 * 24 * 30,
    ):
        self._repo = repo
        self._debug = debug
        self._algorithm = algorithm
        self._private_key = private_key
        self._public_key = public_key
        self._access_token_cookie_name = access_token_cookie_name
        self._access_token_expiration = access_token_expiration
        self._refresh_token_cookie_name = refresh_token_cookie_name
        self._refresh_token_expiration = refresh_token_expiration

    def _create_token(
        self, payload: dict, token_type: str, expiration_delta: int
    ) -> str:
        iat = datetime.now(timezone.utc)
        exp = iat + timedelta(seconds=expiration_delta)

        payload.update(
            {
                "iat": iat,
                "exp": exp,
                "type": token_type,
            }
        )

        return jwt.encode(payload, self._private_key, algorithm=self._algorithm)

    def create_access_token(self, payload: dict) -> str:
        return self._create_token(payload, "access", self._access_token_expiration)

    def create_refresh_token(self, payload: dict) -> str:
        return self._create_token(payload, "refresh", self._refresh_token_expiration)

    def get_access_token_from_request(self, request: Request) -> Optional[str]:
        return request.cookies.get(self._access_token_cookie_name)

    def get_refresh_token_from_request(self, request: Request) -> Optional[str]:
        return request.cookies.get(self._refresh_token_cookie_name)

    def decode_token(self, token: str, leeway: int = 0) -> Optional[dict]:
        if token:
            try:
                payload = jwt.decode(
                    token,
                    self._public_key,
                    leeway=leeway,
                    algorithms=[self._algorithm],
                )
                return payload
            except Exception:
                return None

        return None

    async def _active_blackout_exists(self, iat: int) -> bool:
        ts = await self._repo.get_blackout_ts()
        return ts is not None and ts >= iat

    async def _user_in_blacklist(self, id: int) -> bool:
        # NOTE: maybe move logic here
        return await self._repo.user_was_recently_banned(id)

    async def _user_was_kicked(self, id: int, iat: int) -> bool:
        # NOTE: maybe move logic here
        return await self._repo.user_was_kicked(id, iat)

    async def token_is_valid(self, id: int, iat: int) -> bool:
        issues = await asyncio.gather(
            *(
                self._active_blackout_exists(iat),
                self._user_in_blacklist(id),
                self._user_was_kicked(id, iat),
            )
        )
        return not any(issues)

    async def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        data = self.decode_token(refresh_token)
        if data is None or data.get("type") != "refresh":
            return None

        user = await self._repo.get(data.get("id"))
        if user is None or not user.get("active"):
            return None

        if await self._active_blackout_exists(data.get("iat")):
            return None

        payload = TokenPayload(**user)

        return self.create_access_token(payload.dict())

    def _set_cookie(
        self, response: Response, key: str, value: str, expires: int
    ) -> None:
        response.set_cookie(
            key=key,
            value=value,
            expires=expires,
            secure=not self._debug,
            httponly=True,
        )

    def set_access_cookie(self, response: Response, value: str) -> None:
        response.set_cookie(
            key=self._access_token_cookie_name,
            value=value,
            expires=self._access_token_expiration,
            secure=not self._debug,
            httponly=True,
        )

    def _set_refresh_cookie(self, response: Response, value: str) -> None:
        response.set_cookie(
            key=self._refresh_token_cookie_name,
            value=value,
            expires=self._refresh_token_expiration,
            secure=not self._debug,
            httponly=True,
        )

    def set_login_response(
        self, response: Response, access_token: str, refresh_token: str
    ) -> None:
        self.set_access_cookie(response, access_token)
        self._set_refresh_cookie(response, refresh_token)

    def set_logout_response(self, response: Response) -> None:
        response.delete_cookie(self._access_token_cookie_name)
        response.delete_cookie(self._refresh_token_cookie_name)

    async def get_user(self, request: Request) -> Optional[User]:
        access_token = self.get_access_token_from_request(request)
        if access_token is not None:
            data = self.decode_token(access_token)
            if await self.token_is_valid(data.get("id"), data.get("iat")):
                user = User(data)
                return user

        return None
