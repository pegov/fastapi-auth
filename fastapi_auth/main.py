from typing import Callable, Iterable, Optional, Type

from fastapi import APIRouter, FastAPI, HTTPException, Request

from fastapi_auth.backend.abc.authorization import AbstractAuthorization
from fastapi_auth.backend.abc.cache import AbstractCacheClient
from fastapi_auth.backend.abc.captcha import AbstractCaptchaClient
from fastapi_auth.backend.abc.db import AbstractDatabaseClient
from fastapi_auth.backend.abc.email import AbstractEmailClient
from fastapi_auth.backend.abc.jwt import AbstractJWTBackend
from fastapi_auth.backend.abc.oauth import AbstractOAuthProvider
from fastapi_auth.backend.abc.password import AbstractPasswordBackend
from fastapi_auth.backend.abc.transport import AbstractTransport
from fastapi_auth.backend.abc.validator import AbstractValidator
from fastapi_auth.errors import AuthorizationError, TokenDecodingError
from fastapi_auth.jwt import JWT, TokenParams
from fastapi_auth.models.user import Anonim, BaseUser, User
from fastapi_auth.repo import Repo
from fastapi_auth.routers import (
    get_admin_router,
    get_auth_router,
    get_email_router,
    get_me_router,
    get_oauth_router,
    get_password_router,
)
from fastapi_auth.routers.token import get_token_router
from fastapi_auth.services.admin import AdminService
from fastapi_auth.services.auth import AuthService
from fastapi_auth.services.email import EmailService
from fastapi_auth.services.me import MeService
from fastapi_auth.services.oauth import OAuthService
from fastapi_auth.services.password import PasswordService
from fastapi_auth.services.token import TokenService
from fastapi_auth.validator import GlobalValidator


class FastAPIAuth:
    def __init__(
        self,
        app: FastAPI,
        cache: AbstractCacheClient,
        jwt_backend: AbstractJWTBackend,
        access_token_expiration: int,
        transport: AbstractTransport,
        authorization: AbstractAuthorization,
        anonim_model: Type[Anonim] = Anonim,
    ) -> None:
        self.repo = Repo(
            None,  # type: ignore
            cache,
            access_token_expiration,
            0,
        )
        self._jwt = JWT(jwt_backend, access_token_expiration, 0)
        self._transport = transport
        self._authorization = authorization

        self._anonim_model = anonim_model

        app.state._fastapi_auth = self

    async def get_user(self, request: Request) -> BaseUser:
        try:
            token = self._transport.get_access_token(request)
            payload = self._jwt.decode_token(token)
            user = User(**payload)
            await self._authorization.authorize(self.repo, user, "access")
            return user
        except (TokenDecodingError, AuthorizationError):
            return Anonim()

    async def get_authenticated_user(self, request: Request) -> BaseUser:
        user = await self.get_user(request)
        if user.is_authenticated():
            return user

        raise HTTPException(401)

    async def admin_required(self, request: Request) -> None:
        user = await self.get_user(request)
        if user.is_authenticated() and user.is_admin():
            return

        raise HTTPException(403)

    async def role_required(self, request: Request, role: str) -> None:
        user = await self.get_user(request)
        if user.is_authenticated() and user.has_role(role):
            return

        raise HTTPException(403)


class FastAPIAuthApp(FastAPIAuth):
    def __init__(
        self,
        app: FastAPI,
        db: AbstractDatabaseClient,
        cache: AbstractCacheClient,
        jwt_backend: AbstractJWTBackend,
        token_params: TokenParams,
        access_token_expiration: int,
        refresh_token_expiration: int,
        transport: AbstractTransport,
        authorization: AbstractAuthorization,
        oauth_providers: Iterable[AbstractOAuthProvider],
        password_backend: AbstractPasswordBackend,
        email_client: AbstractEmailClient,
        captcha_client: AbstractCaptchaClient,
        validator: Optional[AbstractValidator] = None,
        on_create_action: Optional[Callable] = None,
        on_update_action: Optional[Callable] = None,
        enable_register_captcha: bool = True,
        enable_forgot_password_captcha: bool = True,
        oauth_path_prefix: str = "/auth",
        oauth_message_path: str = "/oauth",
        origin: str = "http://127.0.0.1",
        debug: bool = False,
    ) -> None:
        self._app = app
        self.repo = Repo(
            db,
            cache,
            access_token_expiration,
            refresh_token_expiration,
        )
        self._jwt = JWT(
            jwt_backend,
            access_token_expiration,
            refresh_token_expiration,
        )
        self._token_params = token_params
        self._transport = transport
        self._oauth_providers = oauth_providers
        self._authorization = authorization
        self._password_backend = password_backend
        self._email_client = email_client
        self._captcha_client = captcha_client

        if validator is not None:
            GlobalValidator.set(validator)

        self._on_create_action = on_create_action
        self._on_update_action = on_update_action

        self._enable_register_captcha = enable_register_captcha
        self._enable_forgot_password_captcha = enable_forgot_password_captcha

        self._debug = debug
        self._origin = origin

        self._oauth_callback_prefix = oauth_path_prefix
        self._oauth_message_path = oauth_message_path

        app.state._fastapi_auth = self

    def include_routers(self, api_prefix: str) -> None:
        self._app.include_router(self.get_auth_router(), prefix=api_prefix)
        self._app.include_router(self.get_token_router(), prefix=api_prefix)
        self._app.include_router(self.get_password_router(), prefix=api_prefix)
        self._app.include_router(self.get_admin_router(), prefix=api_prefix)
        self._app.include_router(self.get_me_router(), prefix=api_prefix)
        self._app.include_router(self.get_email_router(), prefix=api_prefix)
        self._app.include_router(
            self.get_oauth_router(), prefix=self._oauth_callback_prefix
        )

    def get_auth_router(self) -> APIRouter:
        service = AuthService(
            repo=self.repo,
            jwt=self._jwt,
            token_params=self._token_params,
            authorization=self._authorization,
            password_backend=self._password_backend,
            email_client=self._email_client,
            captcha_client=self._captcha_client,
            debug=self._debug,
        )
        return get_auth_router(
            service,
            self._jwt,
            self._transport,
            self._on_create_action,
        )

    def get_password_router(self) -> APIRouter:
        service = PasswordService(
            repo=self.repo,
            jwt=self._jwt,
            token_params=self._token_params,
            password_backend=self._password_backend,
            email_client=self._email_client,
            captcha_client=self._captcha_client,
            debug=self._debug,
        )
        return get_password_router(service)

    def get_oauth_router(self) -> APIRouter:
        service = OAuthService(
            repo=self.repo,
            jwt=self._jwt,
            token_params=self._token_params,
            oauth_providers=self._oauth_providers,
            origin=self._origin,
            path_prefix=self._oauth_callback_prefix,
        )
        return get_oauth_router(
            service,
            self._jwt,
            self._transport,
            self._oauth_message_path,
            self._on_create_action,
        )

    def get_admin_router(self) -> APIRouter:
        service = AdminService(self.repo)
        return get_admin_router(service)

    def get_me_router(self) -> APIRouter:
        service = MeService(
            repo=self.repo,
            jwt=self._jwt,
            token_params=self._token_params,
            email_client=self._email_client,
        )
        return get_me_router(
            service,
            self._on_update_action,
            self._debug,
        )

    def get_email_router(self) -> APIRouter:
        service = EmailService(
            repo=self.repo,
            jwt=self._jwt,
            token_params=self._token_params,
            email_client=self._email_client,
        )
        return get_email_router(service)

    def get_token_router(self) -> APIRouter:
        service = TokenService(self.repo, self._authorization)
        return get_token_router(
            service,
            self._jwt,
            self._transport,
        )
