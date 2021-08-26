from typing import Iterable, Union


class BaseCacheBackend:
    async def get(self, key: str) -> str:
        raise NotImplementedError

    async def delete(self, key: str) -> None:
        raise NotImplementedError

    async def keys(self, match: str) -> Iterable[str]:
        raise NotImplementedError

    async def set(
        self, key: str, value: Union[str, bytes, int], expire: int = 0
    ) -> None:
        raise NotImplementedError

    async def setnx(self, key: str, value: Union[str, bytes, int], expire: int) -> None:
        raise NotImplementedError

    async def incr(self, key: str) -> int:
        raise NotImplementedError
