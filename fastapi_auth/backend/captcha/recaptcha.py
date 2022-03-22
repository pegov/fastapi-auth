from typing import Optional

from httpx import AsyncClient

from fastapi_auth.backend.abc.captcha import AbstractCaptchaClient


class RecaptchaClient(AbstractCaptchaClient):
    def __init__(self, secret: str) -> None:
        self._secret = secret

    async def validate(self, captcha: Optional[str]) -> bool:
        if captcha is None:
            return False

        async with AsyncClient(base_url="https://www.google.com/") as client:
            payload = {
                "secret": self._secret,
                "response": captcha,
            }
            response = await client.post("/recaptcha/api/siteverify", data=payload)
            return response.json().get("success")
