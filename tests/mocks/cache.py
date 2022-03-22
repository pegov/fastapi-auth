from typing import Optional, Union

from fastapi_auth.backend.abc.cache import AbstractCacheClient


class MockCacheClient(AbstractCacheClient):
    def __init__(self) -> None:
        self.db: dict = {}

    async def get(self, key: str) -> Optional[str]:
        return self.db.get(key)

    async def delete(self, key: str) -> None:
        self.db.pop(key, None)

    async def set(self, key: str, value: Union[str, bytes, int], ex: int) -> None:
        self.db[key] = value

    async def setnx(self, key: str, value: Union[str, bytes, int], ex: int) -> bool:
        if self.db.get(key) is None:
            self.db[key] = value
            return True

        return False

    async def incr(self, key: str) -> int:
        v = self.db.get(key)
        if v is None:
            self.db[key] = 1
            return 1
        else:
            new_v = v + 1
            self.db[key] = new_v
            return new_v

    async def expire(self, key: str, ex: int) -> None:
        pass
