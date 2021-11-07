from typing import Callable, Optional

from fastapi import APIRouter, Depends, Request
from fastapi.exceptions import HTTPException

from fastapi_auth.backend.abc import AbstractCaptchaBackend, AbstractEmailBackend
from fastapi_auth.detail import HTTPExceptionDetail
from fastapi_auth.logging import logger
from fastapi_auth.models.password import (
    PasswordChange,
    PasswordForgot,
    PasswordReset,
    PasswordSet,
    PasswordStatus,
)
from fastapi_auth.repo import AuthRepo
from fastapi_auth.services.password import set_password
from fastapi_auth.user import User
from fastapi_auth.utils.password import verify_password
from fastapi_auth.utils.string import create_random_string, hash_string


def get_password_router(
    repo: AuthRepo,
    email_backend: AbstractEmailBackend,
    captcha_backend: Optional[AbstractCaptchaBackend],
    get_authenticated_user: Callable,
    debug: bool,
    enable_captcha: bool,
):
    router = APIRouter()

    @router.post("/password/forgot", name="password:forgot_password")
    async def password_forgot_password(
        *,
        data_in: PasswordForgot,
        request: Request,
    ):
        if (
            not debug
            and enable_captcha
            and not await captcha_backend.validate_captcha(data_in.captcha)
        ):
            raise HTTPException(400, detail=HTTPExceptionDetail.CAPTCHA_IS_NOT_VALID)

        log = {
            "action": "reset_password",
            "email": data_in.email,
            "ip": request.client.host,
        }
        logger.info(log)

        item = await repo.get_by_email(data_in.email)
        if item is None:
            raise HTTPException(404)

        # NOTE: allow users without password to reset password anyway

        id = item.get("id")

        if not await repo.is_password_reset_available(id):
            raise HTTPException(429, detail="reset before")

        email = item.get("email")

        token = create_random_string()
        token_hash = hash_string(token)

        await repo.set_password_reset_token(id, token_hash)
        await email_backend.request_password_reset(email, token)

    @router.get(
        "/password/status",
        response_model=PasswordStatus,
        name="password:get_password_status",
    )
    async def password_get_password_status(
        *,
        user: User = Depends(get_authenticated_user),
    ):
        item = await repo.get(user.id)
        if item.get("provider") is not None and item.get("password") is None:
            return {"has_password": False}
        return {"has_password": True}

    @router.post("/password/set", name="password:set_password")
    async def password_set_password(
        *,
        user: User = Depends(get_authenticated_user),
        data_in: PasswordSet,
    ):
        item = await repo.get(user.id)
        if item.get("password") is not None:
            raise HTTPException(400, detail=HTTPExceptionDetail.PASSWORD_ALREADY_EXISTS)

        await set_password(repo, user.id, data_in.password1)

    @router.post("/password/change", name="password:change_password")
    async def password_change_password(
        *,
        user: User = Depends(get_authenticated_user),
        data_in: PasswordChange,
    ):
        item = await repo.get(user.id)
        if item.get("password") is None:
            raise HTTPException(400, detail=HTTPExceptionDetail.PASSWORD_IS_NOT_SET)

        old_password_hash = item.get("password")
        if not verify_password(data_in.old_password, old_password_hash):
            raise HTTPException(400, detail=HTTPExceptionDetail.INCORRECT_OLD_PASSWORD)

        await set_password(repo, user.id, data_in.password1)

    @router.post("/password/reset", name="password:reset_password")
    async def password_reset_password(
        *,
        data_in: PasswordReset,
    ):
        token_hash = hash_string(data_in.token)
        id = await repo.get_id_for_password_reset(token_hash)
        if id is None:
            raise HTTPException(404)

        await set_password(repo, id, data_in.password1)

    return router
