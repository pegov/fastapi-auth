from string import ascii_letters, digits, punctuation
from typing import List

from starlette.config import Config

config = Config()

JWT_ALGORITHM = "RS256"

DEBUG: bool = config("DEBUG", cast=bool, default=False)

# validation

TIME_DELTA: int = 3

MIN_USERNAME_LENGTH: int = 3
MAX_USERNAME_LENGTH: int = 20

MIN_PASSWORD_LENGTH: int = 6
MAX_PASSWORD_LENGTH: int = 32

russian_letters = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя"
USERNAME_CHARS = "".join([ascii_letters, russian_letters, digits, " -_"])
PASSWORD_CHARS = "".join([ascii_letters, digits, punctuation])

WRONG_USERNAMES: List[str] = [
    "edit",
    "notifications",
    "settings",
    "message",
    "messages",
    "change_info",
]

LOGIN_RATELIMIT: int = 30  # per minute

EMAIL_CONFIRMATION_TIMEOUT: int = 1800
EMAIL_CONFIRMATION_MAX: int = 2

PASSWORD_RESET_TIMEOUT: int = 1800
PASSWORD_RESET_MAX: int = 2
PASSWORD_RESET_LIFETIME: int = 60 * 60 * 2
