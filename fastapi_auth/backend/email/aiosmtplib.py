from email.message import EmailMessage

import aiosmtplib

from fastapi_auth.backend.abc.email import AbstractEmailClient


class AIOSMTPLibEmailClient(AbstractEmailClient):
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
        check_old_email_subject: str,
        check_old_email_message: str,
        check_new_email_subject: str,
        check_new_email_message: str,
        oauth_account_removal_subject: str,
        oauth_account_removal_message: str,
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

        self._check_old_email_subject = check_old_email_subject
        self._check_old_email_message = check_old_email_message
        self._check_new_email_subject = check_new_email_subject
        self._check_new_email_message = check_new_email_message

        self._oauth_account_removal_subject = oauth_account_removal_subject
        self._oauth_account_removal_message = oauth_account_removal_message

    async def _send_email(self, email: str, subject: str, message: str) -> None:
        msg = EmailMessage()
        msg["From"] = f"{self._display_name} <{self._username}>"
        msg["To"] = email
        msg["Subject"] = subject
        msg.set_content(message, subtype="html")

        await aiosmtplib.send(
            msg,
            hostname=self._hostname,
            username=self._username,
            password=self._password,
            port=self._port,
            timeout=20,
            use_tls=True,
        )

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

    async def check_old_email(self, email: str, token: str) -> None:
        await self._send_email(
            email,
            self._check_old_email_subject,
            self._check_old_email_message.format(token),
        )

    async def check_new_email(self, email: str, token: str) -> None:
        await self._send_email(
            email,
            self._check_new_email_subject,
            self._check_new_email_message.format(token),
        )

    async def request_oauth_account_removal(self, email: str, token: str) -> None:
        await self._send_email(
            email,
            self._oauth_account_removal_subject,
            self._oauth_account_removal_message.format(token),
        )
