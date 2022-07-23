from typing import Callable

from fastapi import APIRouter, Depends
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
    WrongTokenTypeError,
)
from fastapi_auth.models.password import (
    PasswordChangeRequest,
    PasswordForgotRequest,
    PasswordResetRequest,
    PasswordSetRequest,
    PasswordStatusResponse,
)
from fastapi_auth.models.user import User
from fastapi_auth.repo import Repo
from fastapi_auth.services.password import PasswordService


def get_password_router(get_repo: Callable, service: PasswordService):
    router = APIRouter()

    @router.post("/password/forgot", name="password:forgot")
    async def password_forgot(
        *,
        data_in: PasswordForgotRequest,
        repo: Repo = Depends(get_repo),
    ):
        try:
            await service.forgot(repo, data_in)
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
        repo: Repo = Depends(get_repo),
        user: User = Depends(get_authenticated_user),
    ):
        return await service.get_status(repo, user)

    @router.post("/password/set", name="password:set")
    async def password_set(
        *,
        data_in: PasswordSetRequest,
        repo: Repo = Depends(get_repo),
        user: User = Depends(get_authenticated_user),
    ):
        try:
            await service.set(repo, data_in, user)
        except PasswordAlreadyExistsError:  # pragma: no cover
            raise HTTPException(400, detail=Detail.PASSWORD_ALREADY_EXISTS)

    @router.post("/password/change", name="password:change")
    async def password_change(
        *,
        data_in: PasswordChangeRequest,
        repo: Repo = Depends(get_repo),
        user: User = Depends(get_authenticated_user),
    ):
        try:
            await service.change(repo, data_in, user)
        except PasswordNotSetError:  # pragma: no cover
            raise HTTPException(400, detail=Detail.PASSWORD_NOT_SET)
        except InvalidPasswordError:  # pragma: no cover
            raise HTTPException(400, detail=Detail.INCORRECT_OLD_PASSWORD)

    @router.post("/password/reset", name="password:reset")
    async def password_reset(
        *,
        data_in: PasswordResetRequest,
        repo: Repo = Depends(get_repo),
    ):
        try:
            await service.reset(repo, data_in)
        except WrongTokenTypeError:
            raise HTTPException(400, detail=Detail.WRONG_TOKEN_TYPE)
        except TokenAlreadyUsedError:  # pragma: no cover
            raise HTTPException(400, detail=Detail.TOKEN_ALREADY_USED)

    return router
