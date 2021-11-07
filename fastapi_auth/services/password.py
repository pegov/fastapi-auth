from fastapi_auth.repo import AuthRepo
from fastapi_auth.utils.password import get_password_hash


async def set_password(
    repo: AuthRepo,
    id: int,
    password: str,
) -> None:
    password_hash = get_password_hash(password)
    await repo.set_password(id, password_hash)
