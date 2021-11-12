from typing import Callable, Iterable, Optional, Type

from fastapi import APIRouter, FastAPI, HTTPException, Request

from fastapi_auth.backend.abc import (
    AbstractCaptchaBackend,
    AbstractEmailBackend,
    AbstractJWTAuthentication,
    AbstractOAuthProvider,
    AbstractUserValidator,
)
from fastapi_auth.models.auth import BaseTokenPayload, TokenPayload
from fastapi_auth.repo import AuthRepo
from fastapi_auth.routers import (
    get_admin_router,
    get_auth_router,
    get_oauth_router,
    get_password_router,
    get_users_router,
    get_verify_router,
)
from fastapi_auth.user import User
from fastapi_auth.validator import Validator


class FastAPIAuth:
    def __init__(
        self,
        app: FastAPI,
        auth_backend: AbstractJWTAuthentication,
    ) -> None:
        self._auth_backend = auth_backend
        app.state._fastapi_auth = self

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


class FastAPIAuthApp(FastAPIAuth):
    def __init__(
        self,
        app: FastAPI,
        auth_backend: AbstractJWTAuthentication,
        repo: AuthRepo,
        email_backend: AbstractEmailBackend,
        captcha_backend: Optional[AbstractCaptchaBackend],
        oauth_providers: Iterable[AbstractOAuthProvider] = [],
        user_token_payload_model: Type[BaseTokenPayload] = TokenPayload,
        user_model_validator: Optional[AbstractUserValidator] = None,
        user_create_hook: Optional[Callable[[dict], None]] = None,
        change_username_callback: Optional[Callable[[Request, int, str], None]] = None,
        enable_register_captcha: bool = True,
        enable_forgot_password_captcha: bool = False,
        debug: bool = False,
        origin: str = "http://127.0.0.1",
        oauth_create_redirect_path_prefix: str = "/auth",  # same as router prefix
        oauth_error_redirect_path: str = "/oauth",
    ):
        super().__init__(app, auth_backend)
        self.repo = repo
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

        self._oauth_create_redirect_path_prefix = oauth_create_redirect_path_prefix
        self._oauth_error_redirect_path = oauth_error_redirect_path

    @property
    def auth_router(self) -> APIRouter:
        return get_auth_router(
            repo=self.repo,
            auth_backend=self._auth_backend,
            captcha_backend=self._captcha_backend,
            email_backend=self._email_backend,
            get_authenticated_user=self.get_authenticated_user,
            user_token_payload_model=self._user_token_payload_model,
            user_create_hook=self._user_create_hook,
            debug=self._debug,
            enable_captcha=self._enable_register_captcha,
        )

    @property
    def password_router(self) -> APIRouter:
        return get_password_router(
            repo=self.repo,
            email_backend=self._email_backend,
            captcha_backend=self._captcha_backend,
            get_authenticated_user=self.get_authenticated_user,
            debug=self._debug,
            enable_captcha=self._enable_forgot_password_captcha,
        )

    @property
    def oauth_router(self) -> APIRouter:
        return get_oauth_router(
            repo=self.repo,
            auth_backend=self._auth_backend,
            oauth_providers=self._oauth_providers,
            user_token_payload_model=self._user_token_payload_model,
            user_create_hook=self._user_create_hook,
            origin=self._origin,
            create_redirect_path_prefix=self._oauth_create_redirect_path_prefix,
            error_redirect_path=self._oauth_error_redirect_path,
        )

    @property
    def admin_router(self) -> APIRouter:
        return get_admin_router(
            repo=self.repo,
            admin_required=self.admin_required,
        )

    @property
    def users_router(self) -> APIRouter:
        return get_users_router(
            repo=self.repo,
            get_authenticated_user=self.get_authenticated_user,
            change_username_callback=self._change_username_callback,
        )

    @property
    def verify_router(self) -> APIRouter:
        return get_verify_router(
            repo=self.repo,
            email_backend=self._email_backend,
            get_authenticated_user=self.get_authenticated_user,
        )


async def get_user(request: Request) -> User:
    auth: FastAPIAuth = request.app.state._fastapi_auth
    return await auth.get_user(request)


async def get_authenticated_user(request: Request) -> User:
    auth: FastAPIAuth = request.app.state._fastapi_auth
    return await auth.get_authenticated_user(request)


async def admin_required(request: Request) -> None:
    auth: FastAPIAuth = request.app.state._fastapi_auth
    await auth.admin_required(request)
