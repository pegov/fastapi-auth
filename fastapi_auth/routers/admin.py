from datetime import datetime
from typing import Callable

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from fastapi_auth.models.admin import Blacklist, Blackout, UpdateUser, UserInfo
from fastapi_auth.repo import AuthRepo


def get_router(
    repo: AuthRepo,
    admin_required: Callable,
) -> APIRouter:
    router = APIRouter()

    @router.get(
        "/blacklist",
        dependencies=[Depends(admin_required)],
        response_model=Blacklist,
        name="admin:get_blacklist",
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
        dependencies=[Depends(admin_required)],
        response_model=Blackout,
        name="admin:get_blackout",
    )
    async def admin_get_blackout():
        return await repo.get_blackout()

    @router.post(
        "/blackout",
        dependencies=[Depends(admin_required)],
        name="admin:set_blackout",
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
        "/{id}/kick",
        dependencies=[Depends(admin_required)],
        name="admin:kick",
    )
    async def admin_kick(id: int):
        await repo.kick(id)

    @router.get(
        "/{id}",
        dependencies=[Depends(admin_required)],
        name="admin:get_user",
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
        dependencies=[Depends(admin_required)],
        name="admin:update_user",
    )
    async def admin_update_user(id: int, data_in: UpdateUser):
        user = await repo.get(id)
        if user is None:
            raise HTTPException(404)

        await repo.update(id, data_in.dict(exclude_none=True))

        # TODO: if username or active => logout

    return router
