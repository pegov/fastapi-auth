from typing import Callable, Optional

from fastapi import APIRouter, Depends, Request
from fastapi.exceptions import HTTPException

from fastapi_auth.backend.captcha.base import BaseCaptchaBackend
from fastapi_auth.backend.email.base import BaseEmailBackend
from fastapi_auth.logging import logger
from fastapi_auth.models.password import (
    PasswordChange,
    PasswordForgot,
    PasswordHasPasswordResponse,
    PasswordReset,
    PasswordSet,
)
from fastapi_auth.repo import AuthRepo
from fastapi_auth.services.password import (
    get_id_for_password_reset,
    reset_password,
    set_password,
)
from fastapi_auth.user import User
from fastapi_auth.utils.password import verify_password


def get_router(
    repo: AuthRepo,
    email_backend: BaseEmailBackend,
    captcha_backend: Optional[BaseCaptchaBackend],
    get_authenticated_user: Callable,
    debug: bool,
    enable_captcha: bool,
):
    router = APIRouter()

    @router.post("/forgot_password")
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
            raise HTTPException(422, detail="captcha")

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

        await reset_password(repo, email_backend, id, email)

    @router.get("/password", response_model=PasswordHasPasswordResponse)
    async def password_has_password(
        *,
        user: User = Depends(get_authenticated_user),
    ):
        item = await repo.get(user.id)
        if item.get("provider") is not None and item.get("password") is None:
            return {"has_password": False}
        return {"has_password": True}

    @router.post("/password")
    async def password_set_password(
        *,
        user: User = Depends(get_authenticated_user),
        data_in: PasswordSet,
    ):
        item = await repo.get(user.id)
        if item.get("password") is not None:
            raise HTTPException(422)

        await set_password(repo, user.id, data_in)

    @router.put("/password")
    async def password_change_password(
        *,
        user: User = Depends(get_authenticated_user),
        data_in: PasswordChange,
    ):
        item = await repo.get(user.id)
        if item.get("password") is None:
            raise HTTPException(422)

        old_password_hash = item.get("password")
        if not verify_password(data_in.old_password, old_password_hash):
            raise HTTPException(401)

        await set_password(repo, user.id, data_in)

    @router.post("/password/{token}")
    async def password_reset_password(
        *,
        token: str,
        data_in: PasswordReset,
    ):
        id = await get_id_for_password_reset(repo, token)
        if id is None:
            raise HTTPException(404)

        await set_password(repo, id, data_in)

    return router
