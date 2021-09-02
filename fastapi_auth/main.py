from typing import Callable, Iterable, Optional, Type

from fastapi import APIRouter, HTTPException, Request

from fastapi_auth.backend.auth import BaseJWTAuthentication
from fastapi_auth.backend.captcha import BaseCaptchaBackend
from fastapi_auth.backend.email import BaseEmailBackend
from fastapi_auth.backend.oauth import BaseOAuthProvider
from fastapi_auth.backend.validator import BaseUserValidator
from fastapi_auth.models.auth import BaseUserTokenPayload, UserTokenPayload
from fastapi_auth.repo import AuthRepo
from fastapi_auth.routers import (
    get_admin_router,
    get_auth_router,
    get_oauth_router,
    get_password_router,
)
from fastapi_auth.user import User
from fastapi_auth.validator import Validator


class Auth:
    def __init__(
        self,
        auth_backend: BaseJWTAuthentication,
    ) -> None:
        self._auth_backend = auth_backend

    async def get_user(self, request: Request) -> User:
        user = await self._auth_backend.get_user(request)
        if user is not None:
            return user

        return User()

    async def get_authenticated_user(self, request: Request) -> User:
        user = await self._auth_backend.get_user(request)
        if user is not None:
            return user

        raise HTTPException(401)

    async def admin_required(self, request: Request) -> None:
        user = await self._auth_backend.get_user(request)
        if user is not None and user.is_admin:
            return

        raise HTTPException(403)


class AuthApp(Auth):
    def __init__(
        self,
        repo: AuthRepo,
        auth_backend: BaseJWTAuthentication,
        email_backend: BaseEmailBackend,
        captcha_backend: Optional[BaseCaptchaBackend],
        oauth_providers: Iterable[BaseOAuthProvider] = [],
        user_token_payload_model: Type[BaseUserTokenPayload] = UserTokenPayload,
        user_model_validator: Optional[BaseUserValidator] = None,
        user_create_hook: Optional[Callable[[dict], None]] = None,
        change_username_callback: Optional[Callable[[int, str], None]] = None,
        enable_register_captcha: bool = True,
        enable_forgot_password_captcha: bool = False,
        debug: bool = False,
        origin: str = "http://127.0.0.1",
    ):
        self._repo = repo
        self._auth_backend = auth_backend
        self._email_backend = email_backend
        self._captcha_backend = captcha_backend
        self._oauth_providers = oauth_providers

        self._user_token_payload_model = user_token_payload_model
        if user_model_validator is not None:
            Validator.set(user_model_validator)

        self._user_create_hook = user_create_hook
        self._change_username_callback = change_username_callback

        self._enable_register_captcha = enable_register_captcha
        self._enable_forgot_password_captcha = enable_forgot_password_captcha

        self._debug = debug
        self._origin = origin

    @property
    def auth_router(self) -> APIRouter:
        return get_auth_router(
            repo=self._repo,
            auth_backend=self._auth_backend,
            captcha_backend=self._captcha_backend,
            email_backend=self._email_backend,
            get_authenticated_user=self.get_authenticated_user,
            user_token_payload_model=self._user_token_payload_model,
            user_create_hook=self._user_create_hook,
            change_username_callback=self._change_username_callback,
            debug=self._debug,
            enable_captcha=self._enable_register_captcha,
        )

    @property
    def password_router(self) -> APIRouter:
        return get_password_router(
            repo=self._repo,
            email_backend=self._email_backend,
            captcha_backend=self._captcha_backend,
            get_authenticated_user=self.get_authenticated_user,
            debug=self._debug,
            enable_captcha=self._enable_forgot_password_captcha,
        )

    @property
    def oauth_router(self) -> APIRouter:
        return get_oauth_router(
            repo=self._repo,
            auth_backend=self._auth_backend,
            oauth_providers=self._oauth_providers,
            user_token_payload_model=self._user_token_payload_model,
            user_create_hook=self._user_create_hook,
            origin=self._origin,
        )

    @property
    def admin_router(self) -> APIRouter:
        return get_admin_router(
            repo=self._repo,
            admin_required=self.admin_required,
        )
