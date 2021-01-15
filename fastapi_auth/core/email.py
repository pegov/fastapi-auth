from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib


class EmailClient:
    def __init__(
        self,
        username: str,
        host: str,
        password: str,
        tls: int,
        language: str,
        base_url: str,
        site: str,
    ):
        self._username = username
        self._host = host
        self._password = password
        self._tls = tls
        self._language = language
        self._base_url = base_url
        self._site = site

    async def _send_email(self, email: str, subject: str, message: str) -> None:
        msg = MIMEMultipart()
        msg["From"] = self._username
        msg["To"] = email
        msg["Subject"] = subject

        msg.attach(MIMEText(message, "html"))
        await aiosmtplib.send(
            msg,
            hostname=self._host,
            username=self._username,
            password=self._password,
            port=self._tls,
            timeout=30,
            start_tls=True,
        )

        del msg

    async def send_confirmation_email(self, email: str, secret_string: str) -> None:
        if self._language == "RU":
            subject = "Подтвердите email"
            msg = f"""Добро пожаловать на <a href="{self._base_url}">{self._site}</a>!<br /><br />Чтобы завершить регистрацию <a href="{self._base_url}/confirm?token={secret_string}">щелкните здесь</a><br /><br />С уважением,<br />администрация сайта <a href="{self._base_url}">{self._site}</a>"""
        else:
            subject = "Confirm email"
            msg = f"""Welcome to <a href="{self._base_url}">{self._site}</a>!<br /><br /><a href="{self._base_url}/confirm?token={secret_string}">Click here</a> to complete your sing up<br /><br />Thanks,<br />{self._site} team"""
        await self._send_email(email, subject, msg)

    async def send_forgot_password_email(self, email: str, secret_string: str) -> None:
        if self._language == "RU":
            subject = "Забыли пароль"
            msg = f"""Кто-то запросил сброс пароля на вашем аккаунте в <a href="{self._base_url}">{self._site}</a><br /><br />
            Если это были вы, <a href="{self._base_url}/reset_password?token={secret_string}">щелкните здесь</a><br /><br /><br /><br />Если это были не вы, можете проигнорировать это письмо.<br /><br />С уважением,<br />администрация сайта <a href="{self._base_url}">{self._site}</a>"""
        else:
            subject = "Forgot password"
            msg = f"""Password reset has been requested for <a href="{self._base_url}">{self._site}</a><br /><br />
            If it was you who did it, <a href="{self._base_url}/reset_password?token={secret_string}">click here</a><br /><br /><br /><br />If it was not you, ignore this letter.<br /><br />Thanks,<br />{self._site} team"""
        await self._send_email(email, subject, msg)
