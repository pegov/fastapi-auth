from datetime import datetime
from typing import Optional, Tuple

from fastapi_auth.backend.abc import AbstractCacheBackend, AbstractDBBackend


async def _reached_ratelimit(
    cache: AbstractCacheBackend,
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

    await cache.set(rate_key, 1, ex=interval)
    return False


class AuthBase:
    def __init__(
        self,
        db: Optional[AbstractDBBackend],
        cache: AbstractCacheBackend,
        access_expiration: int = 60 * 60 * 6,
        login_ratelimit: int = 30,
        login_timeout: int = 60,
        password_reset_max: int = 2,
        password_reset_timeout: int = 60 * 60,
        password_reset_lifetime: int = 60 * 60,
        verification_ratelimit: int = 2,
    ) -> None:
        self._db = db
        self._cache = cache
        self._access_expiration = access_expiration

        self._login_ratelimit = login_ratelimit
        self._login_timeout = login_timeout

        self._password_reset_max = password_reset_max
        self._password_reset_timeout = password_reset_timeout
        self._password_reset_lifetime = password_reset_lifetime

        self._verification_ratelimit = verification_ratelimit


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
            await self._cache.set(timeout_key, 1, ex=self._login_timeout)

        return False


class AuthEmailMixin(AuthCRUDMixin):
    async def is_verification_available(self, id: int) -> bool:
        key = f"users:confirm:count:{id}"
        return not await _reached_ratelimit(
            self._cache, key, self._verification_ratelimit, 1800
        )

    async def request_verification(self, email: str, token_hash: str) -> None:
        await self._db.request_verification(email, token_hash)

    async def verify(self, token_hash: str) -> bool:
        return await self._db.verify(token_hash)


class AuthAccountMixin(AuthCRUDMixin):
    async def change_username(self, id: int, new_username: str) -> None:
        await self.update(id, {"username": new_username})

    async def change_email(self, id: int, new_email: str) -> None:
        await self.update(id, {"email": new_email, "verified": False})


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
        await self._cache.set(key, id, ex=self._password_reset_lifetime)

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
            await self._cache.set(key, 1, ex=self._access_expiration)
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

        await self._cache.set(key, now, ex=self._access_expiration)

    async def get_blackout_status(self) -> dict:
        ts = await self._cache.get("users:blackout")
        if ts is not None:
            return {
                "active": True,
                "date": datetime.utcfromtimestamp(int(ts)),
            }

        return {
            "active": False,
        }

    async def activate_blackout(self) -> None:
        ts = int(datetime.utcnow().timestamp())
        await self._cache.set("users:blackout", ts)

    async def deactivate_blackout(self) -> None:
        await self._cache.delete("users:blackout")

    async def set_permissions(self) -> None:
        pass


class AuthRepo(
    AuthBruteforceProtectionMixin,
    AuthEmailMixin,
    AuthAccountMixin,
    AuthPasswordMixin,
    AuthAdminMixin,
):
    pass
