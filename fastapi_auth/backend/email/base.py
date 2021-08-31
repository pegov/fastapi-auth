class BaseEmailBackend:
    async def request_verification(self, email: str, token: str) -> None:
        raise NotImplementedError

    async def request_password_reset(self, email: str, token: str) -> None:
        raise NotImplementedError
