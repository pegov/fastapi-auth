from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

from fastapi_auth.backend.abc import AbstractEmailBackend


class AIOSMTPLibEmailBackend(AbstractEmailBackend):
    def __init__(
        self,
        hostname: str,
        username: str,
        password: str,
        port: int,
        display_name: str,
        verification_subject: str,
        verification_message: str,
        forgot_password_subject: str,
        forgot_password_message: str,
    ) -> None:
        self._hostname = hostname
        self._username = username
        self._password = password
        self._port = port

        self._display_name = display_name
        self._verification_subject = verification_subject
        self._verification_message = verification_message
        self._forgot_password_subject = forgot_password_subject
        self._forgot_password_message = forgot_password_message

    async def _send_email(self, email: str, subject: str, message: str) -> None:
        msg = MIMEMultipart()
        msg["From"] = f"{self._display_name} <{self._username}>"
        msg["To"] = email
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "html"))

        await aiosmtplib.send(
            msg,
            hostname=self._hostname,
            username=self._username,
            password=self._password,
            port=self._port,
            timeout=20,
            use_tls=True,
        )

        del msg

    async def request_verification(self, email: str, token: str) -> None:
        await self._send_email(
            email,
            self._verification_subject,
            self._verification_message.format(token),
        )

    async def request_password_reset(self, email: str, token: str) -> None:
        await self._send_email(
            email,
            self._forgot_password_subject,
            self._forgot_password_message.format(token),
        )
