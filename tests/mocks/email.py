from fastapi_auth.backend.abc.email import AbstractEmailClient


class MockEmailClient(AbstractEmailClient):
    async def request_verification(self, email: str, token: str) -> None:
        pass

    async def request_password_reset(self, email: str, token: str) -> None:
        pass

    async def check_old_email(self, email: str, token: str) -> None:
        pass

    async def check_new_email(self, email: str, token: str) -> None:
        pass

    async def request_oauth_account_removal(self, email: str, token: str) -> None:
        pass
