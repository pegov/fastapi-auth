from datetime import datetime, timezone
from typing import List

from fastapi_auth.models.admin import MassLogoutStatusResponse
from fastapi_auth.models.user import UserUpdate
from fastapi_auth.repo import Repo
from fastapi_auth.types import UID


class AdminService:
    def __init__(self, repo: Repo) -> None:
        self._repo = repo

    async def ban(self, id: UID) -> None:
        await self._repo.ban(id)

    async def unban(self, id: UID) -> None:
        await self._repo.unban(id)

    async def kick(self, id: UID) -> None:
        await self._repo.kick(id)

    async def unkick(self, id: UID) -> None:
        await self._repo.unkick(id)

    async def set_roles(self, id: UID, roles: List[str]) -> None:
        await self._repo.update(id, UserUpdate(roles=roles).to_update_dict())

    async def get_mass_logout_status(self) -> MassLogoutStatusResponse:
        ts = await self._repo.get_mass_logout_ts()
        if ts is None:
            return MassLogoutStatusResponse(active=False)

        date = datetime.fromtimestamp(ts, tz=timezone.utc)

        return MassLogoutStatusResponse(active=True, date=date)

    async def activate_mass_logout(self) -> None:
        await self._repo.activate_mass_logout()

    async def deactivate_mass_logout(self) -> None:
        await self._repo.deactivate_mass_logout()
