import asyncio
from typing import Callable, Optional, Type

from fastapi import APIRouter, Depends, Request, Response
from fastapi.exceptions import HTTPException
from fastapi.responses import ORJSONResponse

from fastapi_auth.backend.auth.base import BaseJWTAuthentication
from fastapi_auth.backend.captcha import BaseCaptchaBackend
from fastapi_auth.backend.email import BaseEmailBackend
from fastapi_auth.detail import HTTPExceptionDetail
from fastapi_auth.models.auth import (
    BaseUserTokenPayload,
    UserAccount,
    UserCreate,
    UserLogin,
    UserRegister,
    UserTokenPayload,
    UserTokenRefreshResponse,
    UserUpdateAccount,
    UserVerificationStatusResponse,
)
from fastapi_auth.repo import AuthRepo
from fastapi_auth.services.auth import request_verification
from fastapi_auth.user import User
from fastapi_auth.utils.password import get_password_hash, verify_password
from fastapi_auth.utils.string import hash_string


def get_router(
    repo: AuthRepo,
    auth_backend: BaseJWTAuthentication,
    captcha_backend: Optional[BaseCaptchaBackend],
    email_backend: BaseEmailBackend,
    get_authenticated_user: Callable,
    user_token_payload_model: Type[BaseUserTokenPayload],
    user_create_hook: Optional[Callable[[dict], None]],
    change_username_callback: Optional[Callable[[int, str], None]],
    debug: bool,
    enable_captcha: bool,
) -> APIRouter:
    router = APIRouter()

    @router.post("/register", name="auth:register")
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
            raise HTTPException(400, detail=HTTPExceptionDetail.CAPTCHA_IS_NOT_VALID)

        existing_email = await repo.get_by_email(user_in.email)
        if existing_email is not None:
            raise HTTPException(400, detail=HTTPExceptionDetail.EMAIL_ALREADY_EXISTS)

        existing_username = await repo.get_by_username(user_in.username)
        if existing_username is not None:
            raise HTTPException(400, detail=HTTPExceptionDetail.USERNAME_ALREADY_EXISTS)

        password_hash = get_password_hash(user_in.password1)
        user_obj = UserCreate(**user_in.dict(), password=password_hash).dict()
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

    @router.post("/logout", name="auth:logout")
    async def auth_logout(
        *,
        response: Response,
    ):
        auth_backend.set_logout_response(response)

    @router.post("/token", response_model=UserTokenPayload, name="auth:token")
    async def token(
        *,
        user: User = Depends(get_authenticated_user),
    ):
        return user.data

    @router.post(
        "/token/refresh",
        response_model=UserTokenRefreshResponse,
        name="auth:refresh_access_token",
    )
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

    @router.get(
        "/verify",
        response_model=UserVerificationStatusResponse,
        name="auth:get_verification_status",
    )
    async def auth_get_verification_status(
        *,
        user: User = Depends(get_authenticated_user),
    ):
        return await repo.get(user.id)

    @router.post("/verify", name="auth:requets_verification")
    async def auth_request_verification(
        *,
        user: User = Depends(get_authenticated_user),
    ):
        item = await repo.get(user.id)
        if item.get("verified"):
            raise HTTPException(
                400, detail=HTTPExceptionDetail.EMAIL_WAS_ALREADY_VERIFIED
            )

        if not await repo.is_verification_available(user.id):
            raise HTTPException(429)

        await request_verification(repo, email_backend, item.get("email"))

    @router.post("/verify/{token}", name="auth:verify")
    async def auth_verify(*, token: str):
        token_hash = hash_string(token)
        if not await repo.verify(token_hash):
            raise HTTPException(404)

    @router.get(
        "/account",
        name="auth:get_account",
        response_model=UserAccount,
        response_model_exclude_none=True,
    )
    async def auth_get_account(
        *,
        user: User = Depends(get_authenticated_user),
    ):
        return await repo.get(user.id)

    @router.patch("/account", name="auth:update_account")
    async def auth_update_account(
        *,
        user: User = Depends(get_authenticated_user),
        data_in: UserUpdateAccount,
    ):
        item = await repo.get(user.id)

        if data_in.username is not None:
            if data_in.username == item.get("username"):
                raise HTTPException(400, HTTPExceptionDetail.SAME_USERNAME)

            await repo.change_username(user.id, data_in.username)

            if change_username_callback is not None:
                if asyncio.iscoroutinefunction(change_username_callback):
                    await change_username_callback(user.id, data_in.username)  # type: ignore
                else:
                    change_username_callback(user.id, data_in.username)

        if data_in.email is not None:
            if data_in.email == item.get("email"):
                raise HTTPException(400, HTTPExceptionDetail.SAME_EMAIL)
            await repo.change_email(user.id, data_in.email)

    return router
