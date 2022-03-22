from string import ascii_letters, digits

from fastapi_auth.backend.validator.default import DefaultUserValidator

russian_letters = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя"
USERNAME_CHARS = "".join([ascii_letters, russian_letters, digits, "-_"])


class EnRuUserValidator(DefaultUserValidator):
    def validate_username(self, v: str) -> str:
        v = super().validate_username(v)

        if any(letter in ascii_letters for letter in v):
            if any(letter in russian_letters for letter in v):
                raise ValueError("username different letters")
        if any(letter in russian_letters for letter in v):
            if any(letter in ascii_letters for letter in v):
                raise ValueError("username different letters")

        return v
