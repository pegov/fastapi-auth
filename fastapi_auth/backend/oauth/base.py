from typing import Tuple


class BaseOAuthProvider:
    name: str

    def __init__(self, id: str, secret: str) -> None:
        self._id = id
        self._secret = secret

    def create_oauth_uri(self, redirect_uri: str, state: str) -> str:
        raise NotImplementedError

    async def get_user_data(self, redirect_uri: str, code: str) -> Tuple[str, str]:
        """Return sid and email."""
        raise NotImplementedError
