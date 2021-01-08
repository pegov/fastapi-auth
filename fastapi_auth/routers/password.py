from fastapi import APIRouter, Depends, Request

from fastapi_auth.core.user import User, get_authenticated_user
from fastapi_auth.services import PasswordService


def get_router():

    router = APIRouter()

    @router.post("/forgot_password", name="auth:forgot_password")
    async def forgot_password(*, request: Request):
        data = await request.json()
        ip = request.client.host
        service = PasswordService()
        return await service.forgot_password(data, ip)

    @router.get("/password", name="auth:password_status")
    async def password_status(*, user: User = Depends(get_authenticated_user)):
        service = PasswordService(user)
        return await service.password_status()

    @router.post("/password", name="auth:password_set")
    async def password_set(
        *, request: Request, user: User = Depends(get_authenticated_user)
    ):
        data = await request.json()
        service = PasswordService(user)
        return await service.password_set(data)

    @router.post("/password/{token}")
    async def password_reset(*, token: str, request: Request):
        data = await request.json()
        service = PasswordService()
        return await service.password_reset(data, token)

    @router.put("/password", name="auth:password_change")
    async def password_change(
        *, request: Request, user: User = Depends(get_authenticated_user)
    ):
        data = await request.json()
        service = PasswordService(user)
        return await service.password_change(data)

    return router
