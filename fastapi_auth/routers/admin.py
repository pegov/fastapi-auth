from datetime import datetime
from typing import Callable

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from fastapi_auth.models.admin import Blacklist, Blackout, UpdateUser, UserInfo
from fastapi_auth.repo import AuthRepo


def get_admin_router(
    repo: AuthRepo,
    admin_required: Callable,
) -> APIRouter:
    router = APIRouter()

    @router.get(
        "/blacklist",
        name="admin:get_blacklist",
        dependencies=[Depends(admin_required)],
        response_model=Blacklist,
    )
    async def admin_get_blacklist():
        return await repo.get_blacklist()

    @router.post(
        "/{id}/ban",
        dependencies=[Depends(admin_required)],
        name="admin:toggle_blacklist",
    )
    async def admin_toggle_blacklist(id: int):
        await repo.toggle_blacklist(id)

    @router.get(
        "/blackout",
        name="admin:get_blackout",
        dependencies=[Depends(admin_required)],
        response_model=Blackout,
    )
    async def admin_get_blackout():
        return await repo.get_blackout()

    @router.post(
        "/blackout",
        name="admin:set_blackout",
        dependencies=[Depends(admin_required)],
    )
    async def admin_set_blackout():
        ts = datetime.utcnow()
        await repo.set_blackout(ts)

    @router.delete(
        "/blackout",
        name="admin:delete_blackout",
        dependencies=[Depends(admin_required)],
    )
    async def admin_delete_blackout():
        await repo.delete_blackout()

    @router.post(
        "/{id}/kick",
        name="admin:kick",
        dependencies=[Depends(admin_required)],
    )
    async def admin_kick(id: int):
        await repo.kick(id)

    @router.get(
        "/{id}",
        name="admin:get_user",
        dependencies=[Depends(admin_required)],
        response_model=UserInfo,
        response_model_exclude_none=True,
    )
    async def admin_get_user(id: int):
        user = await repo.get(id)
        if user is None:
            raise HTTPException(404)
        return user

    @router.patch(
        "/{id}",
        name="admin:update_user",
        dependencies=[Depends(admin_required)],
    )
    async def admin_update_user(id: int, data_in: UpdateUser):
        user = await repo.get(id)
        if user is None:
            raise HTTPException(404)

        await repo.update(id, data_in.dict(exclude_none=True))

        # TODO: if username or active => logout

    return router
