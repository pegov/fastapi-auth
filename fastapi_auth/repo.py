import asyncio
from datetime import datetime
from typing import Callable, Iterable, Optional, Tuple

from fastapi_auth.backend.cache import BaseCacheBackend
from fastapi_auth.backend.db import BaseDBBackend


async def _reached_ratelimit(
    cache,
    rate_key: str,
    ratelimit: int,
    interval: int,
) -> bool:
    rate = await cache.get(rate_key)
    if rate is not None:
        rate = int(rate)
        if rate > ratelimit:
            return True

        await cache.incr(rate_key)
        return False

    await cache.set(rate_key, 1, expire=interval)
    return False


class AuthBase:
    def __init__(
        self,
        db: Optional[BaseDBBackend],
        cache: BaseCacheBackend,
        change_username_callbacks: Iterable[Callable] = [],
        access_expiration: int = 60 * 60 * 6,
        login_ratelimit: int = 30,
        login_timeout: int = 60,
        password_reset_max: int = 2,
        password_reset_timeout: int = 60 * 60,
        password_reset_lifetime: int = 60 * 60,
        email_confirmation_ratelimit: int = 2,
    ) -> None:
        self._db = db
        self._cache = cache
        self._change_username_callbacks = change_username_callbacks
        self._access_expiration = access_expiration

        self._login_ratelimit = login_ratelimit
        self._login_timeout = login_timeout

        self._password_reset_max = password_reset_max
        self._password_reset_timeout = password_reset_timeout
        self._password_reset_lifetime = password_reset_lifetime

        self._email_confirmation_ratelimit = email_confirmation_ratelimit


class AuthCRUDMixin(AuthBase):
    async def get(self, id: int) -> Optional[dict]:
        return await self._db.get(id)

    async def get_by_email(self, email: str) -> Optional[dict]:
        return await self._db.get_by_email(email)

    async def get_by_username(self, username: str) -> Optional[dict]:
        return await self._db.get_by_username(username)

    async def get_by_social(self, provider: str, sid: str) -> Optional[dict]:
        return await self._db.get_by_social(provider, str(sid))

    async def get_by_login(self, login: str) -> Optional[dict]:
        if "@" in login:
            user = await self.get_by_email(login)
            if user is not None:
                return user

        return await self.get_by_username(login)

    async def create(self, obj: dict) -> int:
        return await self._db.create(obj)

    async def update(self, id: int, obj: dict) -> None:
        await self._db.update(id, obj)
        return None

    async def delete(self, id: int) -> None:
        await self._db.delete(id)
        return None

    async def update_last_login(self, id: int) -> None:
        await self.update(id, {"last_login": datetime.utcnow()})

    async def search(
        self, id: int, username: str, p: int, size: int
    ) -> Tuple[dict, int]:
        return await self._db.search(id, username, p, size)


class AuthBruteforceProtectionMixin(AuthBase):
    async def ip_has_timeout(self, ip: str) -> bool:
        timeout_key = f"users:login:timeout:{ip}"
        timeout = await self._cache.get(timeout_key)

        if timeout is not None:
            return True

        rate_key = f"users:login:rate:{ip}"

        if await _reached_ratelimit(self._cache, rate_key, self._login_ratelimit, 60):
            await self._cache.set(timeout_key, 1, expire=self._login_timeout)

        return False


class AuthEmailMixin(AuthCRUDMixin):
    async def is_email_confirmation_available(self, id: int) -> bool:
        key = f"users:confirm:count:{id}"
        return await _reached_ratelimit(
            self, key, self._email_confirmation_ratelimit, 1800
        )

    async def request_email_confirmation(self, email: str, token_hash: str) -> None:
        await self._db.request_email_confirmation(email, token_hash)

    async def confirm_email(self, token_hash: str) -> bool:
        return await self._db.confirm_email(token_hash)


class AuthUsernameMixin(AuthCRUDMixin):
    async def change_username(self, id: int, new_username: str) -> None:
        await self.update(id, {"username": new_username})
        for callback in self._change_username_callbacks:
            if asyncio.iscoroutinefunction(callback):
                await callback(id, new_username)
            else:
                callback(id, new_username)

        return None


class AuthPasswordMixin(AuthCRUDMixin):
    async def set_password(self, id: int, password: str) -> None:
        await self.update(id, {"password": password})

    async def is_password_reset_available(self, id: int) -> bool:
        key = f"users:reset:count:{id}"
        return await _reached_ratelimit(
            self._cache,
            key,
            self._password_reset_max,
            self._password_reset_timeout,
        )  # type: ignore

    async def set_password_reset_token(self, id: int, token_hash: str) -> None:
        key = f"users:reset:token:{token_hash}"
        await self._cache.set(key, id, expire=self._password_reset_lifetime)

    async def get_id_for_password_reset(self, token_hash: str) -> Optional[int]:
        id = await self._cache.get(f"users:reset:token:{token_hash}")
        if id is not None:
            return int(id)
        else:
            return None


class AuthAdminMixin(AuthCRUDMixin):
    async def get_blacklist(self) -> dict:
        blacklist_db = await self._db.get_blacklist()

        blacklist_cache_keys = await self._cache.keys("users:blacklist:*")
        blacklist_cache = []
        for key in blacklist_cache_keys:
            _, _, id, username = key.split(":", maxsplit=3)
            blacklist_cache.append(
                {
                    "id": id,
                    "username": username,
                }
            )

        return {
            "all": blacklist_db,
            "recent": blacklist_cache,
        }

    async def toggle_blacklist(self, id: int) -> None:
        item = await self.get(id)  # type: ignore
        active = item.get("active")
        await self.update(id, {"active": not active})

        username = item.get("username")
        key = f"users:blacklist:{id}:{username}"

        if active:
            await self._cache.set(key, 1, expire=self._access_expiration)
        else:
            await self._cache.delete(key)

    async def user_was_recently_banned(self, id: int) -> bool:
        return bool(await self._cache.get(f"users:blacklist:{id}"))

    async def user_was_kicked(self, id: int, iat: int) -> bool:
        ts = await self._cache.get(f"users:kick:{id}")
        if ts is None:
            return False

        return int(ts) >= iat

    async def kick(self, id: int) -> None:
        key = f"users:kick:{id}"
        now = int(datetime.utcnow().timestamp())

        await self._cache.set(key, now, expire=self._access_expiration)

    async def get_blackout(self) -> Optional[str]:
        return await self._cache.get("users:blackout")

    async def set_blackout(self, ts: int) -> None:
        await self._cache.set("users:blackout", ts)

    async def delete_blackout(self) -> None:
        await self._cache.delete("users:blackout")

    async def set_permissions(self) -> None:
        pass


class AuthRepo(
    AuthBruteforceProtectionMixin,
    AuthEmailMixin,
    AuthUsernameMixin,
    AuthPasswordMixin,
    AuthAdminMixin,
):
    pass