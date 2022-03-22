from abc import ABC, abstractmethod

from fastapi import Request, Response


class AbstractTransport(ABC):
    @abstractmethod
    def login(
        self,
        response: Response,
        access_token: str,
        refresh_token: str,
        access_token_expiration: int,
        refresh_token_expiration: int,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def logout(
        self,
        response: Response,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def refresh_access_token(
        self,
        response: Response,
        token: str,
        expiration: int,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_access_token(
        self,
        request: Request,
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_refresh_token(
        self,
        request: Request,
    ) -> str:
        raise NotImplementedError
