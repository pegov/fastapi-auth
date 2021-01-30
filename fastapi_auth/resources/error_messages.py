from fastapi_auth.core.config import (
    PASSWORD_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    USERNAME_MAX_LENGTH,
    USERNAME_MIN_LENGTH,
)


class ErrorMessages:
    def __init__(
        self,
        language: str,
    ):
        if language == "RU":
            self._full_messages = {
                # models
                "username length": f"Имя от {USERNAME_MIN_LENGTH} до {USERNAME_MAX_LENGTH} символов",
                "username special characters": "Имя не может содержать спец. символы",
                "username wrong": "Это имя зарезервировано и недоступно",
                "username different letters": "Нельзя одновременно использовать латинские и русские символы в имени",
                "password space": "Пароль не может содержать пробелы",
                "password length": f"Пароль от {PASSWORD_MIN_LENGTH} до {PASSWORD_MAX_LENGTH} символов",
                "password mismatch": "Пароли не совпадают",
                "password special": "Пароль может содержать только цифры, буквы и #$%&'()*+,-./:;<=>?@[]^_`{|}~",
                # services
                "existing email": "Такой email уже существует",
                "existing username": "Такое имя уже существует",
                "ban": "Пользователь заблокирован",
                "reset before": "Отправка ещё одного письма возможна через 30 минут",
                "email not found": "Пользователя с таким email не существует",
                "captcha": "Введите каптчу",
                "validation": "Проверьте данные",
                "password already exists": "Пароль уже установлен",
                "password invalid": "Неверный пароль!",
                "username change same": "Новое имя не отличается от старого",
                "server error": "Неизвестная ошибка",
            }
            self._server_error = "Неизвестная ошибка"
        else:
            self._full_messages = {
                # models
                "username length": f"Username can contain from {USERNAME_MIN_LENGTH} to {USERNAME_MAX_LENGTH} symbols",
                "username special characters": "Username can't contain special characters",
                "username wrong": "Wrong username",
                "username different letters": "Username can be only in latin or cyrillic",
                "password space": "Password can't contain spaces",
                "password length": f"Password can contain from {PASSWORD_MIN_LENGTH} to {PASSWORD_MAX_LENGTH} symbols",
                "password mismatch": "Passwords mismatch",
                "password special": "Password can contain only letters, numbers and #$%&'()*+,-./:;<=>?@[]^_`{|}~",
                # services
                "existing email": "Email already exists",
                "existing username": "Username already exists",
                "ban": "User is banned",
                "reset before": "You can send another email in 30 minutes",
                "captcha": "Wrong captcha",
                "validation": "Check data",
                "password already exists": "Password exists",
                "password invalid": "Wrong password!",
                "username change same": "Enter NEW username",
                "server error": "Unknown error",
            }
            self._server_error = "Unknown error"

    def get_error_message(self, msg: str) -> str:
        full_message = self._full_messages.get(msg) or self._server_error
        return full_message


def get_error_message(msg: str, language: str) -> str:
    error_messages = ErrorMessages(language)
    return error_messages.get_error_message(msg)
