from string import ascii_letters, digits, punctuation
from typing import List, Optional

from fastapi_auth.backend.abc.validator import AbstractValidator

USERNAME_CHARS = "".join([ascii_letters, digits, "-_"])
PASSWORD_CHARS = "".join([ascii_letters, digits, punctuation, " "])


class DefaultUserValidator(AbstractValidator):
    def __init__(
        self,
        username_min_length: int = 4,
        username_max_length: int = 20,
        username_chars: str = USERNAME_CHARS,
        letters: str = ascii_letters,
        forbidden_usernames: List[str] = [],
        password_min_length: int = 6,
        password_max_length: int = 32,
        password_chars: str = PASSWORD_CHARS,
    ):
        self._username_min_length = username_min_length
        self._username_max_length = username_max_length
        self._username_chars = username_chars
        self._letters = letters
        self._forbidden_usernames = forbidden_usernames

        self._password_min_length = password_min_length
        self._password_max_length = password_max_length
        self._password_chars = password_chars

    def validate_username(self, v: str) -> str:
        v = v.strip()
        if v in self._forbidden_usernames:
            raise ValueError("username forbidden")
        for letter in v:
            if letter not in self._username_chars:
                raise ValueError("username chars")
        if len(v) < self._username_min_length or len(v) > self._username_max_length:
            raise ValueError("username length")

        if not any(letter in self._letters for letter in v):
            raise ValueError("username must contain letters")

        return v

    def validate_password(self, v: Optional[str], values) -> Optional[str]:
        if v is None:
            return None

        if len(v) < self._password_min_length or len(v) > self._password_max_length:
            raise ValueError("password length")
        if v != values.get("password1"):
            raise ValueError("password mismatch")
        for letter in v:
            if letter not in self._password_chars:
                raise ValueError("password chars")

        return v
