from typing import Union

from fastapi_auth.models.password import PasswordChange, PasswordReset, PasswordSet
from fastapi_auth.repo import AuthRepo
from fastapi_auth.utils.password import get_password_hash


async def set_password(
    repo: AuthRepo, id: int, data_in: Union[PasswordSet, PasswordChange, PasswordReset]
) -> None:
    password_hash = get_password_hash(data_in.password1)
    await repo.set_password(id, password_hash)
