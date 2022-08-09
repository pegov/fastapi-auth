from datetime import datetime, timezone
from typing import Callable

from fastapi import APIRouter, Depends

from fastapi_auth.dependencies import admin_required
from fastapi_auth.models.admin import MassLogoutStatusResponse, RoleCreate, RoleUpdate
from fastapi_auth.models.user import RoleDB
from fastapi_auth.repo import Repo


def get_admin_router(
    get_repo: Callable,
) -> APIRouter:
    router = APIRouter(dependencies=[Depends(admin_required)])

    @router.get(
        "/mass_logout",
        name="admin:get_mass_logout_status",
        response_model=MassLogoutStatusResponse,
    )
    async def admin_get_mass_logout_status(repo: Repo = Depends(get_repo)):
        ts = await repo.admin.get_mass_logout_ts()
        if ts is None:
            return MassLogoutStatusResponse(active=False)

        date = datetime.fromtimestamp(ts, tz=timezone.utc)
        return MassLogoutStatusResponse(active=True, date=date)

    @router.post(
        "/mass_logout",
        name="admin:activate_mass_logout",
    )
    async def admin_activate_mass_logout(repo: Repo = Depends(get_repo)):
        await repo.admin.activate_mass_logout()

    @router.delete(
        "/mass_logout",
        name="admin:deactivate_mass_logout",
    )
    async def admin_deactivate_mass_logout(repo: Repo = Depends(get_repo)):
        await repo.admin.deactivate_mass_logout()

    @router.post(
        "/roles",
        name="admin:create_role",
        response_model=RoleDB,
    )
    async def admin_create_role(data_in: RoleCreate, repo: Repo = Depends(get_repo)):
        await repo.roles.create(data_in.name)
        return await repo.roles.get_by_name(data_in.name)

    @router.get(
        "/roles/{name}",
        name="admin:get_role",
        response_model=RoleDB,
    )
    async def admin_get_role(name: str, repo: Repo = Depends(get_repo)):
        return await repo.roles.get_by_name(name)

    @router.put(
        "/roles/{name}",
        name="admin:update_role",
    )
    async def admin_update_role(
        name: str,
        data_in: RoleUpdate,
        repo: Repo = Depends(get_repo),
    ):
        if data_in.add is not None:
            await repo.roles.add_permission(name, data_in.add)
        if data_in.remove is not None:
            await repo.roles.remove_permission(name, data_in.remove)

    @router.delete(
        "/roles/{name}",
        name="admin:delete_role",
    )
    async def admin_delete_role(name: str, repo: Repo = Depends(get_repo)):
        await repo.roles.delete_by_name(name)

    @router.put(
        "/{id}/roles",
        name="admin:update_user_roles",
    )
    async def admin_update_user_roles(
        id: int,
        data_in: RoleUpdate,
        repo: Repo = Depends(get_repo),
    ):
        if data_in.add is not None:
            await repo.roles.grant(id, data_in.add)
        if data_in.remove is not None:
            await repo.roles.revoke(id, data_in.remove)

    @router.post(
        "/{id}/ban",
        name="admin:ban",
    )
    async def admin_ban(
        *,
        id: int,
        repo: Repo = Depends(get_repo),
    ):
        await repo.admin.ban(id)

    @router.post(
        "/{id}/unban",
        name="admin:unban",
    )
    async def admin_unban(
        *,
        id: int,
        repo: Repo = Depends(get_repo),
    ):
        await repo.admin.unban(id)

    @router.post(
        "/{id}/kick",
        name="admin:kick",
    )
    async def admin_kick(
        *,
        id: int,
        repo: Repo = Depends(get_repo),
    ):
        await repo.admin.kick(id)

    @router.post(
        "/{id}/unkick",
        name="admin:unkick",
    )
    async def admin_unkick(
        *,
        id: int,
        repo: Repo = Depends(get_repo),
    ):
        await repo.admin.unkick(id)

    return router
