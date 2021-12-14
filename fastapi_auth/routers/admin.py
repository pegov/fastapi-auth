from datetime import datetime, timezone
from typing import Callable

from fastapi import APIRouter, Depends

from fastapi_auth.models.admin import Blacklist, Blackout
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
        name="admin:get_blackout_status",
        dependencies=[Depends(admin_required)],
        response_model=Blackout,
    )
    async def admin_get_blackout_status():
        ts = await repo.get_blackout_ts()
        if ts is not None:
            return {
                "active": True,
                "date": datetime.fromtimestamp(ts, tz=timezone.utc),
            }

        return {
            "active": False,
        }

    @router.post(
        "/blackout",
        name="admin:activate_blackout",
        dependencies=[Depends(admin_required)],
    )
    async def admin_activate_blackout():
        await repo.activate_blackout()

    @router.delete(
        "/blackout",
        name="admin:deactivate_blackout",
        dependencies=[Depends(admin_required)],
    )
    async def admin_deactivate_blackout():
        await repo.deactivate_blackout()

    @router.post(
        "/{id}/kick",
        name="admin:kick",
        dependencies=[Depends(admin_required)],
    )
    async def admin_kick(id: int):
        await repo.kick(id)

    return router
