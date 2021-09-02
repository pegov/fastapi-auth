from datetime import datetime
from typing import Callable, Optional

from fastapi import APIRouter, Depends, HTTPException

from fastapi_auth.models.admin import AdminBlacklist, AdminBlackout, AdminUser
from fastapi_auth.repo import AuthRepo


def get_router(
    repo: AuthRepo,
    admin_required: Callable,
) -> APIRouter:
    router = APIRouter()

    @router.get(
        "/blacklist",
        dependencies=[Depends(admin_required)],
        response_model=AdminBlacklist,
        name="admin:blacklist",
    )
    async def admin_get_blacklist():
        return await repo.get_blacklist()

    @router.post("/{id}/blacklist", dependencies=[Depends(admin_required)])
    async def admin_toggle_blacklist(id: int):
        await repo.toggle_blacklist(id)

    @router.get(
        "/blackout",
        dependencies=[Depends(admin_required)],
        response_model=AdminBlackout,
        name="admin:get_blackout",
    )
    async def admin_get_blackout():
        return await repo.get_blackout()

    @router.post(
        "/blackout", dependencies=[Depends(admin_required)], name="admin:set_blackout"
    )
    async def admin_set_blackout():
        ts = datetime.utcnow()
        await repo.set_blackout(ts)

    @router.delete(
        "/blackout",
        dependencies=[Depends(admin_required)],
        name="admin:delete_blackout",
    )
    async def admin_delete_blackout():
        await repo.delete_blackout()

    @router.post(
        "/{id}/kick", dependencies=[Depends(admin_required)], name="admin:kick"
    )
    async def admin_kick(id: int):
        await repo.kick(id)

    @router.get(
        "",
        dependencies=[Depends(admin_required)],
        response_model=AdminUser,
        name="admin:get_users",
    )
    async def admin_get_users(id: Optional[int], username: Optional[str]):
        if id is not None:
            user = await repo.get(id)
            if user is None:
                raise HTTPException(404)

            return user

        if username is not None:
            user = await repo.get_by_username(username)
            if user is None:
                raise HTTPException(404)

            return user

        raise HTTPException(422)

    @router.get(
        "/{id}",
        dependencies=[Depends(admin_required)],
        name="admin:get_user_by_id",
    )
    async def admin_get_user_by_id(id: int):
        return await repo.get(id)

    return router
