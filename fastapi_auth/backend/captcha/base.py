from typing import Optional


class BaseCaptchaBackend:
    _secret: str

    def __init__(self, secret: str) -> None:
        self._secret = secret

    async def validate_captcha(self, captcha: Optional[str]) -> bool:
        raise NotImplementedError
