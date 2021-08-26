from typing import Optional

from httpx import AsyncClient

from .base import BaseCaptchaBackend


class RecaptchaBackend(BaseCaptchaBackend):
    async def validate_captcha(self, captcha: Optional[str]) -> bool:
        if captcha is None:
            return False

        async with AsyncClient(base_url="https://www.google.com/") as client:
            payload = {
                "secret": self._secret,
                "response": captcha,
            }
            response = await client.post("/recaptcha/api/siteverify", data=payload)
            return response.json().get("success")
