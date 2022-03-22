from abc import ABC, abstractmethod


class AbstractValidator(ABC):
    @abstractmethod
    def validate_username(self, v: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def validate_password(self, v: str, values) -> str:
        raise NotImplementedError
