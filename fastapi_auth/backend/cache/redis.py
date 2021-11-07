from typing import Iterable, Optional, Union

from aioredis import Redis

from fastapi_auth.backend.abc import AbstractCacheBackend


class RedisBackend(AbstractCacheBackend):
    def __init__(self, redis: Optional[Redis]) -> None:
        if redis is not None:
            self.set_client(redis)

    def set_client(self, redis: Redis) -> None:
        self._redis = redis

    async def get(self, key: str) -> str:
        return await self._redis.get(key)

    async def delete(self, key: str) -> None:
        await self._redis.delete(key)

    async def keys(self, match: str) -> Iterable[str]:
        return await self._redis.keys(match)

    async def set(self, key: str, value: Union[str, bytes, int], ex: int = 0) -> None:
        await self._redis.set(key, value, ex=ex)

    async def setnx(self, key: str, value: Union[str, bytes, int], ex: int) -> None:
        await self._redis.set(key, value, ex=ex, nx=True)

    async def incr(self, key: str) -> int:
        return await self._redis.incr(key)
