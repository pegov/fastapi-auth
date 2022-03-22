from fastapi import APIRouter, Depends, HTTPException, Request

from fastapi_auth.dependencies import get_authenticated_user
from fastapi_auth.detail import Detail
from fastapi_auth.errors import (
    EmailAlreadyVerifiedError,
    EmailMismatchError,
    TokenDecodingError,
    UserNotFoundError,
    WrongTokenTypeError,
)
from fastapi_auth.models.user import User
from fastapi_auth.models.verify import VerificationStatusResponse
from fastapi_auth.services.verify import VerifyService


def get_verify_router(service: VerifyService) -> APIRouter:
    router = APIRouter()

    @router.get(
        "/verify",
        name="verify:get_status",
        response_model=VerificationStatusResponse,
    )
    async def verify_get_status(
        *,
        user: User = Depends(get_authenticated_user),
    ):
        return await service.get_status(user)

    @router.post("/verify", name="verify:request")
    async def verify_request(
        *,
        request: Request,
        user: User = Depends(get_authenticated_user),
    ):
        try:
            await service.request(user)
        except EmailAlreadyVerifiedError:  # pragma: no cover
            raise HTTPException(400, detail=Detail.EMAIL_ALREADY_VERIFIED)

    @router.post("/verify/{token}", name="verify:check")
    async def verify_check(*, token: str):
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

    return router
