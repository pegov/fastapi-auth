from typing import Callable, Optional, Type

from fastapi import APIRouter, Depends, Request, Response
from fastapi.exceptions import HTTPException
from fastapi.responses import ORJSONResponse

from fastapi_auth.backend.auth.base import BaseJWTAuthentication
from fastapi_auth.backend.captcha import BaseCaptchaBackend
from fastapi_auth.backend.email import BaseEmailBackend
from fastapi_auth.detail import HTTPExceptionDetail
from fastapi_auth.models.auth import (
    BaseUserCreate,
    BaseUserTokenPayload,
    UserChangeUsername,
    UserEmailConfirmationStatusResponse,
    UserLogin,
    UserRegister,
    UserTokenPayload,
    UserTokenRefreshResponse,
)
from fastapi_auth.repo import AuthRepo
from fastapi_auth.services.auth import create, request_email_confirmation
from fastapi_auth.user import User
from fastapi_auth.utils.password import verify_password
from fastapi_auth.utils.string import hash_string


def get_router(
    repo: AuthRepo,
    auth_backend: BaseJWTAuthentication,
    captcha_backend: Optional[BaseCaptchaBackend],
    email_backend: BaseEmailBackend,
    get_authenticated_user: Callable,
    user_create_model: Type[BaseUserCreate],
    user_token_payload_model: Type[BaseUserTokenPayload],
    user_create_hook: Optional[Callable[[dict], None]],
    debug: bool,
    enable_captcha: bool,
) -> APIRouter:
    router = APIRouter()

    @router.post("/register")
    async def auth_register(
        *,
        user_in: UserRegister,
        response: Response,
    ):
        if (
            not debug
            and enable_captcha
            and not await captcha_backend.validate_captcha(user_in.captcha)
        ):
            raise HTTPException(422, detail=HTTPExceptionDetail.CAPTCHA_IS_NOT_VALID)

        existing_email = await repo.get_by_email(user_in.email)
        if existing_email is not None:
            raise HTTPException(422, detail=HTTPExceptionDetail.EMAIL_ALREADY_EXISTS)

        existing_username = await repo.get_by_username(user_in.username)
        if existing_username is not None:
            raise HTTPException(422, detail=HTTPExceptionDetail.USERNAME_ALREADY_EXISTS)

        user_token_payload = await create(
            repo,
            user_in,
            user_create_model,
            user_create_hook,
            user_token_payload_model,
        )

        await request_email_confirmation(repo, email_backend, user_in.email)

        access_token, refresh_token = auth_backend.create_tokens(
            user_token_payload.dict()
        )
        auth_backend.set_login_response(response, access_token, refresh_token)

    @router.post("/login")
    async def auth_login(
        *,
        request: Request,
        user_in: UserLogin,
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
        if not verify_password(user_in.password, password_hash):
            raise HTTPException(401)

        user_token_payload = UserTokenPayload(**user)
        access_token, refresh_token = auth_backend.create_tokens(
            user_token_payload.dict()
        )
        auth_backend.set_login_response(response, access_token, refresh_token)

    @router.post("/logout")
    async def auth_logout(
        *,
        response: Response,
    ):
        auth_backend.set_logout_response(response)

    @router.post("/token", response_model=UserTokenPayload)
    async def token(
        *,
        user: User = Depends(get_authenticated_user),
    ):
        return user.data

    @router.post("/token/refresh", response_model=UserTokenRefreshResponse)
    async def auth_refresh_access_token(
        *,
        request: Request,
        response: Response,
    ):
        refresh_token = auth_backend.get_refresh_token_from_request(request)
        if refresh_token is None:
            raise HTTPException(401)

        access_token = await auth_backend.refresh_access_token(refresh_token)
        if access_token is None:
            raise HTTPException(401)

        auth_backend.set_access_cookie(response, access_token)
        return ORJSONResponse({"access_token": access_token})

    @router.get("/confirm", response_model=UserEmailConfirmationStatusResponse)
    async def auth_get_email_confirmation_status(
        *,
        user: User = Depends(get_authenticated_user),
    ):
        return await repo.get(user.id)

    @router.post("/confirm")
    async def auth_request_email_confirmation(
        *,
        user: User = Depends(get_authenticated_user),
    ):
        item = await repo.get(user.id)
        if item.get("confirmed"):
            raise HTTPException(
                422, detail=HTTPExceptionDetail.EMAIL_WAS_ALREADY_CONFIRMED
            )

        if not await repo.is_email_confirmation_available(user.id):
            raise HTTPException(429)

        await request_email_confirmation(repo, email_backend, item.get("email"))

    @router.post("/confirm/{token}")
    async def auth_confirm_email(*, token: str):
        token_hash = hash_string(token)
        if not await repo.confirm_email(token_hash):
            raise HTTPException(404)

    @router.post("{id}/change_username")
    async def auth_change_username(
        *,
        user: User = Depends(get_authenticated_user),
        data_in: UserChangeUsername,
    ):
        await repo.change_username(user.id, data_in.username)

    return router
