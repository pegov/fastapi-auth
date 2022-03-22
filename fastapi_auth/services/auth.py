import asyncio
from datetime import datetime, timezone
from typing import Optional

from fastapi_auth.backend.abc.authorization import AbstractAuthorization
from fastapi_auth.backend.abc.captcha import AbstractCaptchaClient
from fastapi_auth.backend.abc.email import AbstractEmailClient
from fastapi_auth.backend.abc.password import AbstractPasswordBackend
from fastapi_auth.errors import (
    EmailAlreadyExistsError,
    InvalidCaptchaError,
    InvalidPasswordError,
    PasswordNotSetError,
    TimeoutError,
    UsernameAlreadyExistsError,
    UserNotActiveError,
    UserNotFoundError,
)
from fastapi_auth.jwt import JWT, TokenParams
from fastapi_auth.models.auth import LoginRequest, RegisterRequest
from fastapi_auth.models.user import User, UserCreate, UserDB, UserUpdate
from fastapi_auth.repo import Repo
from fastapi_auth.services.verify import request_verification


class AuthService:
    def __init__(
        self,
        repo: Repo,
        jwt: JWT,
        token_params: TokenParams,
        authorization: AbstractAuthorization,
        password_backend: AbstractPasswordBackend,
        email_client: Optional[AbstractEmailClient],
        captcha_client: Optional[AbstractCaptchaClient],
        debug: bool,
    ):
        self._repo = repo
        self._jwt = jwt
        self._tp = token_params
        self._authorization = authorization
        self._password_backend = password_backend
        self._email_client = email_client
        self._captcha_client = captcha_client
        self._debug = debug

    async def register(
        self,
        data_in: RegisterRequest,
        ip: str,
    ) -> UserDB:
        if (
            not self._debug
            and self._captcha_client is not None
            and not await self._captcha_client.validate(data_in.captcha)
        ):
            raise InvalidCaptchaError

        try:
            await self._repo.get_by_email(data_in.email)
            raise EmailAlreadyExistsError
        except UserNotFoundError:
            pass

        try:
            await self._repo.get_by_username(data_in.username)
            raise UsernameAlreadyExistsError
        except UserNotFoundError:
            pass

        new_user = UserCreate(
            **data_in.dict(),
            password=self._password_backend.hash(data_in.password1),
        )

        id = await self._repo.create(new_user.dict(exclude_none=True))

        user = UserDB(**new_user.dict(), id=id)

        if self._email_client is not None:
            try:
                await request_verification(
                    self._jwt,
                    self._tp,
                    self._email_client,
                    user.id,
                    user.email,
                )
            except Exception:  # pragma: no cover
                pass

        return user

    async def login(
        self,
        data_in: LoginRequest,
        ip: str,
    ) -> UserDB:
        if await self._repo.rate_limit_reached("login", 30, 60, 120, ip):
            raise TimeoutError

        user = await self._repo.get_by_login(data_in.login)
        if user is None:
            raise UserNotFoundError

        if user.password is None:
            raise PasswordNotSetError

        if not self._password_backend.verify(data_in.password, user.password):
            raise InvalidPasswordError

        if not user.active:
            raise UserNotActiveError

        last_login_update_obj = UserUpdate(
            last_login=datetime.now(timezone.utc),
        )
        asyncio.create_task(
            self._repo.update(
                user.id,
                last_login_update_obj.to_update_dict(),
            )
        )

        return user

    async def authorize(self, user: User) -> UserDB:
        await self._authorization.authorize(self._repo, user, "refresh")
        user_db = await self._repo.get(user.id)
        if not user_db.active:
            raise UserNotActiveError

        return user_db
