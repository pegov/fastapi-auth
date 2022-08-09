from typing import Callable, Iterable, Optional

from fastapi import APIRouter, FastAPI, HTTPException, Request

from fastapi_auth.backend.abc.authorization import AbstractAuthorization
from fastapi_auth.backend.abc.captcha import AbstractCaptchaClient
from fastapi_auth.backend.abc.email import AbstractEmailClient
from fastapi_auth.backend.abc.jwt import AbstractJWTBackend
from fastapi_auth.backend.abc.oauth import AbstractOAuthProvider
from fastapi_auth.backend.abc.password import AbstractPasswordBackend
from fastapi_auth.backend.abc.transport import AbstractTransport
from fastapi_auth.backend.abc.validator import AbstractValidator
from fastapi_auth.dependencies import GlobalDependencies
from fastapi_auth.errors import AuthorizationError, TokenDecodingError
from fastapi_auth.jwt import JWT, TokenParams
from fastapi_auth.models.user import User
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
from fastapi_auth.services.auth import AuthService
from fastapi_auth.services.email import EmailService
from fastapi_auth.services.me import MeService
from fastapi_auth.services.oauth import OAuthService
from fastapi_auth.services.password import PasswordService
from fastapi_auth.validator import GlobalValidator


class FastAPIAuth:
    def __init__(
        self,
        app: FastAPI,
        get_repo,
        jwt_backend: AbstractJWTBackend,
        token_params: TokenParams,
        transport: AbstractTransport,
        authorization: AbstractAuthorization,
    ) -> None:
        self.get_repo = get_repo
        GlobalDependencies.get_repo = get_repo

        self._jwt = JWT(jwt_backend, token_params)
        self._transport = transport
        self._authorization = authorization
        self._token_params = token_params

        app.state._fastapi_auth = self

    async def get_user(self, request: Request, repo: Repo) -> Optional[User]:
        try:
            token = self._transport.get_access_token(request)
            payload = self._jwt.decode_token(token)
            user = User(**payload)
            await self._authorization.authorize(
                repo,
                user,
                self._token_params.access_token_type,
            )
            return user
        except (TokenDecodingError, AuthorizationError):
            return None

    async def get_authenticated_user(self, request: Request, repo: Repo) -> User:
        user = await self.get_user(request, repo)
        if user is not None:
            return user

        raise HTTPException(401)

    async def admin_required(self, request: Request, repo: Repo) -> None:
        user = await self.get_user(request, repo)
        if user is not None and user.is_admin():
            return

        raise HTTPException(403)

    async def role_required(
        self,
        request: Request,
        repo: Repo,
        role: str,
    ) -> None:
        user = await self.get_user(request, repo)
        if user is not None and user.has_role(role):
            return

        raise HTTPException(403)

    async def permission_required(
        self,
        request: Request,
        repo: Repo,
        permission: str,
    ) -> None:
        user = await self.get_user(request, repo)
        if user is not None and user.has_permission(permission):
            return

        raise HTTPException(403)


class FastAPIAuthApp(FastAPIAuth):
    def __init__(
        self,
        app: FastAPI,
        get_repo,
        jwt_backend: AbstractJWTBackend,
        token_params: TokenParams,
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
        self.get_repo = get_repo
        GlobalDependencies.get_repo = get_repo

        self._jwt = JWT(jwt_backend, token_params)
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
            jwt=self._jwt,
            token_params=self._token_params,
            authorization=self._authorization,
            password_backend=self._password_backend,
            email_client=self._email_client,
            captcha_client=self._captcha_client,
            debug=self._debug,
        )
        return get_auth_router(
            self.get_repo,
            service,
            self._jwt,
            self._transport,
            self._token_params,
            self._on_create_action,
        )

    def get_password_router(self) -> APIRouter:
        service = PasswordService(
            jwt=self._jwt,
            token_params=self._token_params,
            password_backend=self._password_backend,
            email_client=self._email_client,
            captcha_client=self._captcha_client,
            debug=self._debug,
        )
        return get_password_router(self.get_repo, service)

    def get_oauth_router(self) -> APIRouter:
        service = OAuthService(
            jwt=self._jwt,
            token_params=self._token_params,
            oauth_providers=self._oauth_providers,
            origin=self._origin,
            path_prefix=self._oauth_callback_prefix,
        )
        return get_oauth_router(
            self.get_repo,
            service,
            self._jwt,
            self._token_params,
            self._transport,
            self._oauth_message_path,
            self._on_create_action,
        )

    def get_admin_router(self) -> APIRouter:
        return get_admin_router(self.get_repo)

    def get_me_router(self) -> APIRouter:
        service = MeService(
            jwt=self._jwt,
            token_params=self._token_params,
            email_client=self._email_client,
        )
        return get_me_router(
            self.get_repo,
            service,
            self._on_update_action,
            self._debug,
        )

    def get_email_router(self) -> APIRouter:
        service = EmailService(
            jwt=self._jwt,
            token_params=self._token_params,
            email_client=self._email_client,
        )
        return get_email_router(self.get_repo, service)

    def get_token_router(self) -> APIRouter:
        return get_token_router(
            self.get_repo,
            self._authorization,
            self._jwt,
            self._token_params,
            self._transport,
        )
