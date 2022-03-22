from abc import ABC, abstractmethod


class AbstractJWTBackend(ABC):
    @abstractmethod
    def create_token(self, type: str, payload: dict, expiration: int) -> str:
        raise NotImplementedError

    @abstractmethod
    def decode_token(self, token: str) -> dict:
        raise NotImplementedError
