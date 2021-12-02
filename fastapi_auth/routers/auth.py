import asyncio
from typing import Callable, Optional, Type

from fastapi import APIRouter, Depends, Request, Response
from fastapi.exceptions import HTTPException
from fastapi.responses import ORJSONResponse

from fastapi_auth.backend.abc import (
    AbstractCaptchaBackend,
    AbstractEmailBackend,
    AbstractJWTAuthentication,
)
from fastapi_auth.detail import HTTPExceptionDetail
from fastapi_auth.models.auth import (
    BaseTokenPayload,
    Create,
    Login,
    Register,
    TokenPayload,
    TokenRefreshResponse,
)
from fastapi_auth.repo import AuthRepo
from fastapi_auth.services.verify import request_verification
from fastapi_auth.user import User
from fastapi_auth.utils.password import get_password_hash, verify_password


def get_auth_router(
    repo: AuthRepo,
    auth_backend: AbstractJWTAuthentication,
    captcha_backend: Optional[AbstractCaptchaBackend],
    email_backend: AbstractEmailBackend,
    get_authenticated_user: Callable,
    user_token_payload_model: Type[BaseTokenPayload],
    user_create_hook: Optional[Callable[[dict], None]],
    debug: bool,
    enable_captcha: bool,
) -> APIRouter:
    router = APIRouter()

    @router.post("/register", name="auth:register")
    async def auth_register(
        *,
        user_in: Register,
        response: Response,
    ):
        if (
            not debug
            and enable_captcha
            and not await captcha_backend.validate_captcha(user_in.captcha)
        ):
            raise HTTPException(400, detail=HTTPExceptionDetail.CAPTCHA_IS_NOT_VALID)

        existing_email = await repo.get_by_email(user_in.email)
        if existing_email is not None:
            raise HTTPException(400, detail=HTTPExceptionDetail.EMAIL_ALREADY_EXISTS)

        existing_username = await repo.get_by_username(user_in.username)
        if existing_username is not None:
            raise HTTPException(400, detail=HTTPExceptionDetail.USERNAME_ALREADY_EXISTS)

        password_hash = get_password_hash(user_in.password1)
        user_obj = Create(**user_in.dict(), password=password_hash).dict()
        id = await repo.create(user_obj)
        user_obj.update({"id": id})

        if user_create_hook is not None:
            if asyncio.iscoroutinefunction(user_create_hook):
                await user_create_hook(user_obj)  # type: ignore
            else:
                user_create_hook(user_obj)

        user_token_payload = user_token_payload_model(**user_obj)

        try:
            await request_verification(repo, email_backend, user_in.email)
        except Exception:
            # TODO
            pass

        access_token, refresh_token = auth_backend.create_tokens(
            user_token_payload.dict()
        )
        auth_backend.set_login_response(response, access_token, refresh_token)

    @router.post("/login", name="auth:login")
    async def auth_login(
        *,
        request: Request,
        user_in: Login,
        response: Response,
    ):
        if await repo.ip_has_timeout(request.client.host):
            raise HTTPException(429)

        user = await repo.get_by_login(user_in.login)
        if user is None:
            raise HTTPException(404)

        if not user.get("active"):
            raise HTTPException(401)

        password_hash = user.get("password")
        if not verify_password(user_in.password, password_hash):  # type: ignore
            raise HTTPException(401)

        user_token_payload = TokenPayload(**user)
        access_token, refresh_token = auth_backend.create_tokens(
            user_token_payload.dict()
        )
        auth_backend.set_login_response(response, access_token, refresh_token)

        asyncio.create_task(repo.update_last_login(user.get("id")))  # type: ignore

    @router.post("/logout", name="auth:logout")
    async def auth_logout(
        *,
        response: Response,
    ):
        auth_backend.set_logout_response(response)

    @router.post("/token", response_model=TokenPayload, name="auth:token")
    async def token(
        *,
        user: User = Depends(get_authenticated_user),
    ):
        return user.data

    @router.post(
        "/token/refresh",
        response_model=TokenRefreshResponse,
        name="auth:refresh_access_token",
    )
    async def auth_refresh_access_token(
        *,
        request: Request,
    ):
        refresh_token = auth_backend.get_refresh_token_from_request(request)
        if refresh_token is None:
            raise HTTPException(401)

        access_token = await auth_backend.refresh_access_token(refresh_token)
        if access_token is None:
            raise HTTPException(401)

        response = ORJSONResponse({"access_token": access_token})
        auth_backend.set_access_cookie(response, access_token)
        return response

    return router
