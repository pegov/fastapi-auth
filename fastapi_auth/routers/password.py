from fastapi import APIRouter, Depends, Request
from fastapi.exceptions import HTTPException

from fastapi_auth.dependencies import get_authenticated_user
from fastapi_auth.detail import Detail
from fastapi_auth.errors import (
    InvalidCaptchaError,
    InvalidPasswordError,
    PasswordAlreadyExistsError,
    PasswordNotSetError,
    TimeoutError,
    TokenAlreadyUsedError,
    UserNotFoundError,
)
from fastapi_auth.models.password import (
    PasswordChangeRequest,
    PasswordForgotRequest,
    PasswordResetRequest,
    PasswordSetRequest,
    PasswordStatusResponse,
)
from fastapi_auth.models.user import User
from fastapi_auth.services.password import PasswordService


def get_password_router(service: PasswordService):
    router = APIRouter()

    @router.post("/password/forgot", name="password:forgot")
    async def password_forgot(
        *,
        data_in: PasswordForgotRequest,
    ):
        try:
            await service.forgot(data_in)
        except InvalidCaptchaError:  # pragma: no cover
            raise HTTPException(400, detail=Detail.INVALID_CAPTCHA)
        except UserNotFoundError:  # pragma: no cover
            raise HTTPException(404)
        except TimeoutError:  # pragma: no cover
            raise HTTPException(429)

    @router.get(
        "/password/status",
        name="password:get_status",
        response_model=PasswordStatusResponse,
    )
    async def password_get_status(
        *,
        user: User = Depends(get_authenticated_user),
    ):
        return await service.get_status(user)

    @router.post("/password/set", name="password:set")
    async def password_set(
        *,
        user: User = Depends(get_authenticated_user),
        data_in: PasswordSetRequest,
    ):
        try:
            await service.set(data_in, user)
        except PasswordAlreadyExistsError:  # pragma: no cover
            raise HTTPException(400, detail=Detail.PASSWORD_ALREADY_EXISTS)

    @router.post("/password/change", name="password:change")
    async def password_change(
        *,
        user: User = Depends(get_authenticated_user),
        data_in: PasswordChangeRequest,
    ):
        try:
            await service.change(data_in, user)
        except PasswordNotSetError:  # pragma: no cover
            raise HTTPException(400, detail=Detail.PASSWORD_NOT_SET)
        except InvalidPasswordError:  # pragma: no cover
            raise HTTPException(400, detail=Detail.INCORRECT_OLD_PASSWORD)

    @router.post("/password/reset", name="password:reset")
    async def password_reset(
        *,
        data_in: PasswordResetRequest,
    ):
        try:
            await service.reset(data_in)
        except TokenAlreadyUsedError:  # pragma: no cover
            raise HTTPException(400, detail=Detail.TOKEN_ALREADY_USED)

    return router
