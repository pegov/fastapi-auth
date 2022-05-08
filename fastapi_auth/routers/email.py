from fastapi import APIRouter, Depends, HTTPException, Request

from fastapi_auth.dependencies import get_authenticated_user
from fastapi_auth.detail import Detail
from fastapi_auth.errors import (
    EmailAlreadyVerifiedError,
    EmailMismatchError,
    SameEmailError,
    TokenAlreadyUsedError,
    TokenDecodingError,
    UserNotFoundError,
    WrongTokenTypeError,
)
from fastapi_auth.models.email import ChangeEmailRequest
from fastapi_auth.models.user import User
from fastapi_auth.services.email import EmailService


def get_email_router(service: EmailService) -> APIRouter:
    router = APIRouter(prefix="/email")

    @router.post("/verify", name="email:request_verification")
    async def email_request_verification(
        *,
        request: Request,
        user: User = Depends(get_authenticated_user),
    ):
        try:
            await service.request_verification(user)
        except EmailAlreadyVerifiedError:  # pragma: no cover
            raise HTTPException(400, detail=Detail.EMAIL_ALREADY_VERIFIED)
        except TimeoutError:
            raise HTTPException(429)

    @router.post("/verify/{token}", name="email:verify")
    async def email_verify(*, token: str):
        try:
            await service.verify(token)

        except WrongTokenTypeError:  # pragma: no cover
            raise HTTPException(400, detail=Detail.WRONG_TOKEN_TYPE)
        except EmailAlreadyVerifiedError:  # pragma: no cover
            raise HTTPException(400, detail=Detail.EMAIL_ALREADY_VERIFIED)
        except EmailMismatchError:  # pragma: no cover
            raise HTTPException(400, detail=Detail.EMAIL_MISMATCH)
        except TokenDecodingError:  # pragma: no cover
            raise HTTPException(401)
        except UserNotFoundError:  # pragma: no cover
            raise HTTPException(404)

    @router.post("/change", name="email:request_email_change")
    async def email_request_email_change(
        data_in: ChangeEmailRequest,
        user: User = Depends(get_authenticated_user),
    ):
        try:
            await service.request_email_change(data_in, user)
        except SameEmailError:
            raise HTTPException(400, detail=Detail.SAME_EMAIL)
        except TimeoutError:  # pragma: no cover
            raise HTTPException(429)

    @router.post("/change/old/{token}", name="email:verify_old")
    async def email_change_verify_old(token: str):
        try:
            await service.verify_old(token)

        except WrongTokenTypeError:  # pragma: no cover
            raise HTTPException(400, detail=Detail.WRONG_TOKEN_TYPE)
        except TokenAlreadyUsedError:  # pragma: no cover
            raise HTTPException(400, detail=Detail.TOKEN_ALREADY_USED)

    @router.post("/change/new/{token}", name="email:verify_new")
    async def email_change_verify_new(token: str):
        try:
            await service.verify_new(token)
        except WrongTokenTypeError:  # pragma: no cover
            raise HTTPException(400, detail=Detail.WRONG_TOKEN_TYPE)
        except TokenAlreadyUsedError:  # pragma: no cover
            raise HTTPException(400, detail=Detail.TOKEN_ALREADY_USED)

    return router
