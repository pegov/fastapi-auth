from datetime import datetime, timezone
from typing import Any, List, Optional

from fastapi_auth.backend.abc.cache import AbstractCacheClient
from fastapi_auth.backend.abc.db import AbstractDatabaseClient
from fastapi_auth.errors import TokenAlreadyUsedError, UserNotFoundError
from fastapi_auth.jwt import TokenParams
from fastapi_auth.models.user import OAuthDB, RoleDB, UserCreate, UserDB, UserUpdate


class AdminRepo:
    def __init__(
        self,
        db: AbstractDatabaseClient,
        cache: AbstractCacheClient,
        access_token_expiration: int,
        refresh_token_expiration: int,
        ban_key_prefix: str,
        kick_key_prefix: str,
        mass_logout_key: str,
    ) -> None:
        self.db = db
        self.cache = cache
        self.ban_key_prefix = ban_key_prefix
        self.kick_key_prefix = kick_key_prefix
        self.mass_logout_key = mass_logout_key
        self.access_token_expiration = access_token_expiration
        self.refresh_token_expiration = refresh_token_expiration

    async def ban(self, id: int) -> None:
        await self.db.update(
            id,
            UserUpdate(active=False).to_update_dict(),
        )
        await self.cache.set(
            f"{self.ban_key_prefix}:{id}",
            1,
            ex=self.access_token_expiration,
        )

    async def unban(self, id: int) -> None:
        await self.db.update(
            id,
            UserUpdate(active=True).to_update_dict(),
        )
        await self.cache.delete(f"{self.ban_key_prefix}:{id}")

    async def kick(self, id: int) -> None:
        ts = int(datetime.now(timezone.utc).timestamp())
        await self.cache.set(
            f"{self.kick_key_prefix}:{id}",
            ts,
            ex=self.refresh_token_expiration,
        )

    async def unkick(self, id: int) -> None:
        await self.cache.delete(f"{self.kick_key_prefix}:{id}")

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


class OAuthRepo:
    def __init__(
        self,
        db: AbstractDatabaseClient,
        cache: AbstractCacheClient,
    ) -> None:
        self.db = db
        self.cache = cache

    async def get(self, user_id: int) -> Optional[OAuthDB]:
        return await self.db.oauth.get_by_user_id(user_id)

    async def create(self, user_id: int, provider: str, sid: str) -> None:
        await self.db.oauth.create(user_id, provider, str(sid))

    async def update(self, user_id: int, provider: str, sid: str) -> None:
        await self.db.oauth.update_by_user_id(user_id, provider, str(sid))

    async def delete(self, user_id: int) -> None:
        await self.db.oauth.delete_by_user_id(user_id)


class RolesRepo:
    def __init__(
        self,
        db: AbstractDatabaseClient,
        cache: AbstractCacheClient,
    ) -> None:
        self.db = db
        self.cache = cache

    # NOTE: this is stupid

    async def create(self, name: str) -> int:
        return await self.db.roles.create(name)

    async def get_by_name(self, name: str) -> Optional[RoleDB]:
        return await self.db.roles.get_by_name(name)

    async def add_permission(self, role_name: str, permission_name: str) -> None:
        await self.db.roles.add_permission(role_name, permission_name)

    async def remove_permission(self, role_name: str, permission_name: str) -> None:
        await self.db.roles.remove_permission(role_name, permission_name)

    async def delete_by_name(self, name: str) -> None:
        return await self.db.roles.delete_by_name(name)

    async def grant(self, user_id: int, role_name: str) -> None:
        await self.db.roles.grant(user_id, role_name)

    async def revoke(self, user_id: int, role_name: str) -> None:
        await self.db.roles.revoke(user_id, role_name)

    async def all(self) -> List[RoleDB]:
        return await self.db.roles.all()


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
        tp: TokenParams,
    ) -> None:
        self.db = db
        self.cache = cache
        self.tp = tp
        self.admin = AdminRepo(
            db,
            cache,
            tp.access_token_expiration,
            tp.refresh_token_expiration,
            self.ban_key_prefix,
            self.kick_key_prefix,
            self.mass_logout_key,
        )
        self.oauth = OAuthRepo(db, cache)
        self.roles = RolesRepo(db, cache)

    def _create_obj(self, user: Optional[dict]) -> UserDB:
        if user is None:
            raise UserNotFoundError

        oauth_provider = user.get("provider")
        if oauth_provider is not None:
            oauth = OAuthDB(
                provider=oauth_provider,
                sid=user.get("oauth_sid"),  # type: ignore
            )
        else:
            oauth = None

        return UserDB(**user, oauth=oauth)

    def _user_or_error(self, user: Optional[UserDB]) -> UserDB:
        if user is not None:
            return user

        raise UserNotFoundError

    async def get(self, id: int) -> UserDB:
        user = await self.db.get(id)
        return self._user_or_error(user)

    async def get_by_email(self, email: str) -> UserDB:
        user = await self.db.get_by_email(email)
        return self._user_or_error(user)

    async def get_by_username(self, username: str) -> UserDB:
        user = await self.db.get_by_username(username)
        return self._user_or_error(user)

    async def get_by_login(self, login: str) -> UserDB:
        if "@" in login:
            try:
                return await self.get_by_email(login)
            except UserNotFoundError:
                pass

        return await self.get_by_username(login)

    async def get_by_provider_and_sid(self, provider: str, sid: str) -> UserDB:
        user = await self.db.get_by_provider_and_sid(provider, str(sid))
        return self._user_or_error(user)

    async def create(self, obj: UserCreate) -> int:
        return await self.db.create(obj)

    async def update(self, id: int, obj: dict) -> None:
        await self.db.update(id, obj)

    async def delete(self, id: int) -> None:
        await self.db.delete(id)

    async def user_was_recently_banned(self, id: int) -> bool:
        return bool(await self.cache.get(f"{self.ban_key_prefix}:{id}"))

    async def user_was_kicked(self, id: int, iat: int) -> bool:
        ts = await self.cache.get(f"{self.kick_key_prefix}:{id}")
        if ts is None:
            return False

        return int(ts) >= iat

    async def user_in_mass_logout(self, iat: int) -> bool:
        ts = await self.admin.get_mass_logout_ts()
        if ts is None:
            return False

        return int(ts) >= iat

    async def verify_email(self, email: str) -> bool:
        item = await self.db.get_by_email(email)
        if item is None:
            return False

        await self.db.update(
            item.get("id"),  # type: ignore
            UserUpdate(verified=True).to_update_dict(),
        )
        return True

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
            await self.cache.expire(type, interval)

        if cur >= rate:
            await self.cache.set(timeout_key, 1, ex=timeout)
            return True

        return False
