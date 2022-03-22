import asyncio
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi_auth.backend.abc.cache import AbstractCacheClient
from fastapi_auth.backend.abc.db import AbstractDatabaseClient
from fastapi_auth.errors import TokenAlreadyUsedError, UserNotFoundError
from fastapi_auth.models.user import UserDB, UserUpdate
from fastapi_auth.types import UID


class Repo:
    rate_key_prefix: str = "users:rate"
    used_token_key_prefix: str = "users:used_token"
    timeout_key_prefix: str = "users:timeout"
    mass_logout_key: str = "users:mass_logout"
    ban_key_prefix: str = "users:ban"
    kick_key_prefix: str = "users:kick"

    def __init__(
        self,
        db: AbstractDatabaseClient,
        cache: AbstractCacheClient,
        access_token_expiration: int,
        refresh_token_expiration: int,
    ) -> None:
        self.db = db
        self.cache = cache
        self.access_token_expiration = access_token_expiration
        self.refresh_token_expiration = refresh_token_expiration

    async def get(self, id: UID) -> UserDB:
        return await self.db.get(id)

    async def get_by_email(self, email: str) -> UserDB:
        return await self.db.get_by_email(email)

    async def get_by_username(self, username: str) -> UserDB:
        return await self.db.get_by_username(username)

    async def get_by_login(self, login: str) -> UserDB:
        if "@" in login:
            try:
                return await self.get_by_email(login)
            except UserNotFoundError:
                pass

        return await self.get_by_username(login)

    async def get_by_oauth(self, provider: str, sid: str) -> UserDB:
        return await self.db.get_by_oauth(provider, str(sid))

    async def create(self, obj: dict) -> UID:
        return await self.db.create(obj)

    async def update(self, id: UID, obj: dict) -> None:
        await self.db.update(id, obj)
        return None

    async def delete(self, id: UID) -> None:
        await self.db.delete(id)
        return None

    async def ban(self, id: UID) -> None:
        await self.db.update(
            id,
            UserUpdate(active=False).to_update_dict(),
        )
        await self.cache.set(
            f"{self.ban_key_prefix}:{id}",
            1,
            ex=self.access_token_expiration,
        )

    async def unban(self, id: UID) -> None:
        await self.db.update(
            id,
            UserUpdate(active=True).to_update_dict(),
        )
        await self.cache.delete(f"{self.ban_key_prefix}:{id}")

    async def user_was_recently_banned(self, id: UID) -> bool:
        return bool(await self.cache.get(f"{self.ban_key_prefix}:{id}"))

    async def kick(self, id: UID) -> None:
        ts = int(datetime.now(timezone.utc).timestamp())
        await self.cache.set(
            f"{self.kick_key_prefix}:{id}",
            ts,
            ex=self.refresh_token_expiration,
        )

    async def unkick(self, id: UID) -> None:
        await self.cache.delete(f"{self.kick_key_prefix}:{id}")

    async def user_was_kicked(self, id: UID, iat: int) -> bool:
        ts = await self.cache.get(f"{self.kick_key_prefix}:{id}")
        if ts is None:
            return False

        return int(ts) >= iat

    async def activate_mass_logout(self) -> None:
        ts = int(datetime.now(timezone.utc).timestamp())
        await self.cache.set(
            self.mass_logout_key,
            ts,
            ex=self.refresh_token_expiration,
        )

    async def deactivate_mass_logout(self) -> None:
        await self.cache.delete(self.mass_logout_key)

    async def get_mass_logout_ts(self) -> Optional[int]:
        ts = await self.cache.get(self.mass_logout_key)
        if ts is not None:
            return int(ts)

        return None

    async def user_in_mass_logout(self, iat: int) -> bool:
        ts = await self.get_mass_logout_ts()
        if ts is None:
            return False

        return int(ts) >= iat

    async def verify(self, email: str) -> None:
        item = await self.db.get_by_email(email)

        await self.db.update(
            item.id,
            UserUpdate(verified=True).to_update_dict(),
        )

    async def use_token(self, token: str, ex: int) -> None:
        key = f"users:used_token:{token}"
        res = await self.cache.setnx(key, 1, ex=ex)
        if not res:
            raise TokenAlreadyUsedError

    async def rate_limit_reached(
        self,
        type: str,
        rate: int,
        interval: int,
        timeout: int,
        id: Any,
    ) -> bool:
        timeout_key = f"{self.timeout_key_prefix}:{type}:{id}"
        if await self.cache.get(timeout_key) is not None:
            return True

        cur = await self.cache.incr(f"{self.rate_key_prefix}:{type}:{id}")
        if cur == 1:
            asyncio.create_task(self.cache.expire(type, interval))

        if cur >= rate:
            await self.cache.set(timeout_key, 1, ex=timeout)
            return True

        return False
