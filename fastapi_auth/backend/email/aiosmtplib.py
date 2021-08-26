from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

from .base import BaseEmailBackend


class AIOSMTPLibEmailBackend(BaseEmailBackend):
    def __init__(
        self,
        hostname: str,
        username: str,
        password: str,
        port: int,
        mime_from: str,
        confirmation_subject: str,
        confirmation_message: str,
        forgot_password_subject: str,
        forgot_password_message: str,
    ) -> None:
        self._hostname = hostname
        self._username = username
        self._password = password
        self._port = port

        self._from = mime_from
        self._confirmation_subject = confirmation_subject
        self._confirmationt_message = confirmation_message
        self._forgot_password_subject = forgot_password_subject
        self._forgot_password_message = forgot_password_message

    async def _send_email(self, email: str, subject: str, message: str) -> None:
        msg = MIMEMultipart()
        msg["From"] = self._from
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

    async def send_confirmation_email(self, email: str, token: str) -> None:
        await self._send_email(
            email,
            self._confirmation_subject,
            self._confirmationt_message.format(token),
        )

    async def send_forgot_password_email(self, email: str, token: str) -> None:
        await self._send_email(
            email,
            self._forgot_password_subject,
            self._forgot_password_message.format(token),
        )
