from typing import Callable, Optional

from fastapi import Depends, Request

from fastapi_auth.models.user import User
from fastapi_auth.repo import Repo


class GlobalDependencies:
    get_repo: Callable


async def get_user(
    request: Request,
    repo: Repo = Depends(GlobalDependencies.get_repo),
) -> Optional[User]:
    return await request.app.state._fastapi_auth.get_user(request, repo)


async def get_authenticated_user(
    request: Request,
    repo: Repo = Depends(GlobalDependencies.get_repo),
) -> User:
    return await request.app.state._fastapi_auth.get_authenticated_user(request, repo)


async def admin_required(
    request: Request,
    repo: Repo = Depends(GlobalDependencies.get_repo),
) -> None:
    await request.app.state._fastapi_auth.admin_required(request, repo)


def role_required(role: str):
    async def _role_required(
        request: Request,
        repo: Repo = Depends(GlobalDependencies.get_repo),
    ) -> None:
        await request.app.state._fastapi_auth.role_required(request, repo, role)

    return _role_required


def permission_required(permission: str):
    async def _permission_required(
        request: Request,
        repo: Repo = Depends(GlobalDependencies.get_repo),
    ) -> None:
        await request.app.state._fastapi_auth.permission_required(
            request, repo, permission
        )

    return _permission_required
