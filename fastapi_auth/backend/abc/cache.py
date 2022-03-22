from abc import ABC, abstractmethod
from typing import Optional, Union


class AbstractCacheClient(ABC):
    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, key: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def set(self, key: str, value: Union[str, bytes, int], ex: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def setnx(self, key: str, value: Union[str, bytes, int], ex: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def incr(self, key: str) -> int:
        raise NotImplementedError

    @abstractmethod
    async def expire(self, key: str, ex: int) -> None:
        raise NotImplementedError
