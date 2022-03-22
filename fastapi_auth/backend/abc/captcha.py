from abc import ABC, abstractmethod
from typing import Optional


class AbstractCaptchaClient(ABC):
    @abstractmethod
    async def validate(self, captcha: Optional[str]) -> bool:
        raise NotImplementedError
