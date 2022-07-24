from typing import Optional, Union

from aioredis import Redis

from fastapi_auth.backend.abc.cache import AbstractCacheClient


class RedisClient(AbstractCacheClient):
    def __init__(self, conn: Redis) -> None:
        self._conn = conn

    async def get(self, key: str) -> Optional[str]:
        return await self._conn.get(key)

    async def delete(self, key: str) -> None:
        await self._conn.delete(key)

    async def set(self, key: str, value: Union[str, bytes, int], ex: int) -> None:
        await self._conn.set(key, value, ex=ex)

    async def setnx(self, key: str, value: Union[str, bytes, int], ex: int) -> bool:
        return bool(await self._conn.set(key, value, ex=ex, nx=True))

    async def incr(self, key: str) -> int:
        return await self._conn.incr(key)

    async def expire(self, key: str, ex: int) -> None:
        await self._conn.expire(key, ex)
