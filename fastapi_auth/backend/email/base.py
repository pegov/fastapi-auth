class BaseEmailBackend:
    async def send_confirmation_email(self, email: str, token: str) -> None:
        raise NotImplementedError

    async def send_forgot_password_email(self, email: str, token: str) -> None:
        raise NotImplementedError
