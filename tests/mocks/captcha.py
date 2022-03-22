from typing import Optional

from fastapi_auth.backend.abc.captcha import AbstractCaptchaClient


class MockCaptchaClient(AbstractCaptchaClient):
    async def validate(self, captcha: Optional[str]) -> bool:
        return captcha is not None
