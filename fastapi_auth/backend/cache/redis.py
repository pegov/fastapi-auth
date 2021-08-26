from typing import Iterable, Optional, Union

from aioredis import Redis

from .base import BaseCacheBackend


class RedisBackend(BaseCacheBackend):
    def __init__(self, con: Optional[Redis]) -> None:
        self._redis = con

    def set_con(self, con: Redis) -> None:
        self._redis = con

    async def get(self, key: str) -> str:
        return await self._redis.get(key)

    async def delete(self, key: str) -> None:
        await self._redis.delete(key)

    async def keys(self, match: str) -> Iterable[str]:
        return await self._redis.keys(match)

    async def set(
        self, key: str, value: Union[str, bytes, int], expire: int = 0
    ) -> None:
        await self._redis.set(key, value, expire=expire)

    async def setnx(self, key: str, value: Union[str, bytes, int], expire: int) -> None:
        await self._redis.set(
            key, value, expire=expire, exist=self._redis.SET_IF_NOT_EXIST
        )

    async def incr(self, key: str) -> int:
        return await self._redis.incr(key)