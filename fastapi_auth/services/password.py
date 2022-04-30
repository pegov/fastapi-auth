from typing import Optional
from uuid import UUID

from fastapi_auth.backend.abc.captcha import AbstractCaptchaClient
from fastapi_auth.backend.abc.email import AbstractEmailClient
from fastapi_auth.backend.abc.password import AbstractPasswordBackend
from fastapi_auth.errors import (
    InvalidCaptchaError,
    InvalidPasswordError,
    PasswordAlreadyExistsError,
    PasswordNotSetError,
    TimeoutError,
    WrongTokenTypeError,
)
from fastapi_auth.jwt import JWT, TokenParams
from fastapi_auth.models.password import (
    PasswordChangeRequest,
    PasswordForgotRequest,
    PasswordResetRequest,
    PasswordResetTokenPayload,
    PasswordSetRequest,
    PasswordStatusResponse,
)
from fastapi_auth.models.user import User, UserUpdate
from fastapi_auth.repo import Repo
from fastapi_auth.types import UID


class PasswordService:
    def __init__(
        self,
        repo: Repo,
        jwt: JWT,
        token_params: TokenParams,
        password_backend: AbstractPasswordBackend,
        email_client: AbstractEmailClient,
        captcha_client: Optional[AbstractCaptchaClient],
        debug: bool,
    ):
        self._repo = repo
        self._jwt = jwt
        self._tp = token_params
        self._password_backend = password_backend
        self._email_client = email_client
        self._captcha_client = captcha_client
        self._debug = debug

    async def get_status(
        self,
        user: User,
    ) -> PasswordStatusResponse:
        item = await self._repo.get(user.id)

        has_password = item.password is not None
        return PasswordStatusResponse(has_password=has_password)

    async def set(self, data_in: PasswordSetRequest, user: User) -> None:
        item = await self._repo.get(user.id)

        if item.password is not None:
            raise PasswordAlreadyExistsError

        await self._set(item.id, data_in.password1)

    async def _set(self, id: UID, password: str) -> None:
        password_hash = self._password_backend.hash(password)
        update_user_obj = UserUpdate(password=password_hash).to_update_dict()
        await self._repo.update(id, update_user_obj)

    async def change(self, data_in: PasswordChangeRequest, user: User) -> None:
        user_db = await self._repo.get(user.id)
        if user_db.password is None:
            raise PasswordNotSetError

        if not self._password_backend.verify(data_in.old_password, user_db.password):
            raise InvalidPasswordError

        await self._set(user.id, data_in.password1)

    async def forgot(
        self,
        data_in: PasswordForgotRequest,
    ) -> None:
        if (
            not self._debug
            and self._captcha_client is not None
            and not await self._captcha_client.validate(data_in.captcha)
        ):
            raise InvalidCaptchaError

        item = await self._repo.get_by_email(data_in.email)

        if await self._repo.rate_limit_reached(
            self._tp.reset_password_token_type,
            3,
            60 * 60,
            60 * 30,
            item.id,
        ):
            raise TimeoutError

        token = self._jwt.create_token(
            self._tp.reset_password_token_type,
            {"id": str(item.id) if isinstance(item.id, UUID) else item.id},
            self._tp.reset_password_token_expiration,
        )

        await self._email_client.request_password_reset(item.email, token)

    async def reset(
        self,
        data_in: PasswordResetRequest,
    ) -> UID:
        payload = self._jwt.decode_token(data_in.token)
        obj = PasswordResetTokenPayload(**payload)

        if obj.type != self._tp.reset_password_token_type:
            raise WrongTokenTypeError

        await self._repo.use_token(
            data_in.token, self._tp.reset_password_token_expiration
        )

        await self._set(obj.id, data_in.password1)  # pragma: no cover
        return obj.id
