from typing import Optional, Union

from fastapi_auth.backend.email.base import BaseEmailBackend
from fastapi_auth.models.password import PasswordChange, PasswordReset, PasswordSet
from fastapi_auth.repo import AuthRepo
from fastapi_auth.utils.password import get_password_hash
from fastapi_auth.utils.string import create_random_string, hash_string


async def request_password_reset(
    repo: AuthRepo, email_backend: BaseEmailBackend, id: int, email: str
) -> None:

    token = create_random_string()
    token_hash = hash_string(token)

    await repo.set_password_reset_token(id, token_hash)

    await email_backend.request_password_reset(email, token)


async def set_password(
    repo: AuthRepo, id: int, data_in: Union[PasswordSet, PasswordChange, PasswordReset]
) -> None:
    password_hash = get_password_hash(data_in.password1)
    await repo.set_password(id, password_hash)


async def get_id_for_password_reset(repo: AuthRepo, token: str) -> Optional[int]:
    token_hash = hash_string(token)
    return await repo.get_id_for_password_reset(token_hash)
