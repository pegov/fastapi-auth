from dataclasses import dataclass
from typing import Tuple

from fastapi_auth.backend.abc.jwt import AbstractJWTBackend


@dataclass
class TokenParams:
    reset_password_token_type: str = "reset_password"
    reset_password_token_expiration: int = 60 * 60
    reset_password_rate_limit: int = 2
    reset_password_interval: int = 60 * 60
    reset_password_timeout: int = 60 * 60

    check_old_email_token_type: str = "change_email_old"
    check_new_email_token_type: str = "change_email_new"
    change_email_token_expiration: int = 60 * 20
    change_email_rate_limit: int = 2
    change_email_interval: int = 60 * 60
    change_email_timeout: int = 60 * 60

    add_oauth_account_token_type: str = "add_oauth_account"
    add_oauth_account_token_expiration: int = 60 * 2
    add_oauth_account_limit: int = 8
    add_oauth_account_interval: int = 60 * 30
    add_oauth_account_timeout: int = 60 * 30

    remove_oauth_account_token_type: str = "remove_oauth_account"
    remove_oauth_account_token_expiration: int = 60 * 20
    remove_oauth_account_limit: int = 2
    remove_oauth_account_interval: int = 60 * 30
    remove_oauth_account_timeout: int = 60 * 30

    verify_email_token_type: str = "verify_email"
    verify_email_token_expiration: int = 60 * 60 * 24 * 30
    verify_email_limit: int = 4
    verify_email_interval: int = 60 * 60
    verify_email_timeout: int = 60 * 60


class JWT:
    def __init__(
        self,
        backend: AbstractJWTBackend,
        access_token_expiration: int,
        refresh_token_expiration: int,
    ):
        self._backend = backend
        self.access_token_expiration = access_token_expiration
        self.refresh_token_expiration = refresh_token_expiration

    def decode_token(self, token: str) -> dict:
        return self._backend.decode_token(token)

    def create_token(self, type: str, payload: dict, expiration: int) -> str:
        return self._backend.create_token(type, payload, expiration)

    def create_access_token(
        self,
        payload: dict,
    ) -> str:
        return self._backend.create_token(
            "access", payload, self.access_token_expiration
        )

    def create_refresh_token(self, payload: dict) -> str:
        return self._backend.create_token(
            "refresh", payload, self.refresh_token_expiration
        )

    def create_tokens(self, payload: dict) -> Tuple[str, str]:
        return (
            self.create_access_token(payload),
            self.create_refresh_token(payload),
        )
