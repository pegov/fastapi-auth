from typing import Callable

from fastapi import APIRouter, Depends, HTTPException

from fastapi_auth.backend.abc import AbstractEmailBackend
from fastapi_auth.detail import HTTPExceptionDetail
from fastapi_auth.models.verify import Status
from fastapi_auth.repo import AuthRepo
from fastapi_auth.services.verify import request_verification
from fastapi_auth.user import User
from fastapi_auth.utils.string import hash_string


def get_verify_router(
    repo: AuthRepo,
    get_authenticated_user: Callable,
    email_backend: AbstractEmailBackend,
) -> APIRouter:
    router = APIRouter()

    @router.get(
        "/verify",
        response_model=Status,
        name="verify:get_status",
    )
    async def verify_get_status(
        *,
        user: User = Depends(get_authenticated_user),
    ):
        return await repo.get(user.id)

    @router.post("/verify", name="verify:request")
    async def verify_request(
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

    @router.post("/verify/{token}", name="verify:check")
    async def verify_check(*, token: str):
        token_hash = hash_string(token)
        if not await repo.verify(token_hash):
            raise HTTPException(404)

    return router
