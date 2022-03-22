from typing import Union

from fastapi import Request

from fastapi_auth.models.user import Anonim, User


async def get_user(request: Request) -> Union[User, Anonim]:
    return await request.app.state._fastapi_auth.get_user(request)


async def get_authenticated_user(request: Request) -> User:
    return await request.app.state._fastapi_auth.get_authenticated_user(request)


async def admin_required(request: Request) -> None:
    await request.app.state._fastapi_auth.admin_required(request)


def role_required(role: str):
    async def _role_required(request: Request) -> None:
        await request.app.state._fastapi_auth.role_required(request, role)

    return _role_required
