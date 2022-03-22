from typing import Tuple

from fastapi_auth.backend.abc.oauth import AbstractOAuthProvider


class MockOAuthProvider(AbstractOAuthProvider):
    name: str = "mock"

    def create_oauth_uri(self, redirect_uri: str, state: str) -> str:
        return f"{redirect_uri}?state={state}"

    async def get_user_data(self, redirect_uri: str, code: str) -> Tuple[str, str]:
        return self.name, "4"

    def is_login_only(self) -> bool:
        return False


class MockLoginOnlyOAuthProvider(MockOAuthProvider):
    name: str = "mock_login_only"

    def is_login_only(self) -> bool:
        return True
