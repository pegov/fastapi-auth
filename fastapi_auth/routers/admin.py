from fastapi import APIRouter, Depends

from fastapi_auth.dependencies import admin_required
from fastapi_auth.models.admin import MassLogoutStatusResponse, SetRolesRequest
from fastapi_auth.services.admin import AdminService


def get_admin_router(
    service: AdminService,
) -> APIRouter:
    router = APIRouter(dependencies=[Depends(admin_required)])

    @router.get(
        "/mass_logout",
        name="admin:get_mass_logout_status",
        response_model=MassLogoutStatusResponse,
    )
    async def admin_get_mass_logout_status():
        await service.get_mass_logout_status()

    @router.post(
        "/mass_logout",
        name="admin:activate_mass_logout",
    )
    async def admin_activate_mass_logout():
        await service.activate_mass_logout()

    @router.delete(
        "/mass_logout",
        name="admin:deactivate_mass_logout",
    )
    async def admin_deactivate_mass_logout():
        return await service.deactivate_mass_logout()

    @router.post(
        "/{id}/ban",
        name="admin:ban",
    )
    async def admin_ban(id: int):
        await service.ban(id)

    @router.post(
        "/{id}/unban",
        name="admin:unban",
    )
    async def admin_unban(id: int):
        await service.unban(id)

    @router.post(
        "/{id}/kick",
        name="admin:kick",
    )
    async def admin_kick(id: int):
        await service.kick(id)

    @router.post(
        "/{id}/unkick",
        name="admin:unkick",
    )
    async def admin_unkick(id: int):
        await service.unkick(id)

    @router.put(
        "/{id}/roles",
        name="admin:set_roles",
    )
    async def admin_set_roles(id: int, data_in: SetRolesRequest):
        await service.set_roles(id, data_in.roles)

    return router
