from typing import Optional

from fastapi import Request

from fastapi_auth.models.user import User


async def get_user(request: Request) -> Optional[User]:
    return await request.app.state._fastapi_auth.get_user(request)


async def get_authenticated_user(request: Request) -> User:
    return await request.app.state._fastapi_auth.get_authenticated_user(request)


async def admin_required(request: Request) -> None:
    await request.app.state._fastapi_auth.admin_required(request)


def role_required(role: str):
    async def _role_required(request: Request) -> None:
        await request.app.state._fastapi_auth.role_required(request, role)

    return _role_required


def permission_required(permission: str):
    async def _permission_required(request: Request) -> None:
        await request.app.state._fastapi_auth.permission_required(request, permission)

    return _permission_required
