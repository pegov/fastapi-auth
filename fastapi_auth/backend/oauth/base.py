from fastapi_auth.backend.abc import AbstractOAuthProvider


class BaseOAuthProvider(AbstractOAuthProvider):
    name: str

    def __init__(self, id: str, secret: str) -> None:
        self._id = id
        self._secret = secret
