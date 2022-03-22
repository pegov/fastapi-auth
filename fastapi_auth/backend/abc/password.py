from abc import ABC, abstractmethod


class AbstractPasswordBackend(ABC):
    @abstractmethod
    def verify(self, plain_password: str, hashed_password: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def hash(self, password: str) -> str:
        raise NotImplementedError
