from fastapi_auth.backend.abc.oauth import AbstractOAuthProvider


class BaseOAuthProvider(AbstractOAuthProvider):
    name: str

    def __init__(self, id: str, secret: str, login_only: bool = False) -> None:
        self._id = id
        self._secret = secret
        self._login_only = login_only

    def is_login_only(self) -> bool:
        return self._login_only
