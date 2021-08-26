from string import ascii_letters, digits, punctuation
from typing import List

from fastapi_auth.backend.validator.base import BaseUserValidator

russian_letters = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя"
USERNAME_CHARS = "".join([ascii_letters, russian_letters, digits, "-_"])
PASSWORD_CHARS = "".join([ascii_letters, digits, punctuation])


class StandardUserValidator(BaseUserValidator):
    def __init__(
        self,
        username_min_length: int = 3,
        username_max_length: int = 20,
        username_chars: str = USERNAME_CHARS,
        forbidden_usernames: List[str] = [],
        password_min_length: int = 6,
        password_max_length: int = 32,
        password_chars: str = PASSWORD_CHARS,
    ):
        self._username_min_length = username_min_length
        self._username_max_length = username_max_length
        self._username_chars = username_chars
        self._forbidden_usernames = forbidden_usernames

        self._password_min_length = password_min_length
        self._password_max_length = password_max_length
        self._password_chars = password_chars

    def validate_username(self, v: str) -> str:
        v = v.strip()
        if len(v) < self._username_min_length or len(v) > self._username_max_length:
            raise ValueError("username length")
        for letter in v:
            if letter not in self._username_chars:
                raise ValueError("username chars")
        if v in self._forbidden_usernames:
            raise ValueError("username forbidden")

        if any(letter in ascii_letters for letter in v):
            if any(letter in russian_letters for letter in v):
                raise ValueError("username different letters")
        if any(letter in russian_letters for letter in v):
            if any(letter in ascii_letters for letter in v):
                raise ValueError("username different letters")

        return v

    def validate_password(self, v: str, values) -> str:
        if " " in v:
            raise ValueError("password space")
        if len(v) < self._password_min_length or len(v) > self._password_max_length:
            raise ValueError("password length")
        if v != values.get("password1"):
            raise ValueError("password mismatch")
        for letter in v:
            if letter not in self._password_chars:
                raise ValueError("password chars")

        return v
