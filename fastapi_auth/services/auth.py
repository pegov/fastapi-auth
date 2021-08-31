from fastapi_auth.backend.email.base import BaseEmailBackend
from fastapi_auth.repo import AuthRepo
from fastapi_auth.utils.string import create_random_string, hash_string


async def request_verification(
    repo: AuthRepo, email_backend: BaseEmailBackend, email: str
) -> None:
    token = create_random_string()
    token_hash = hash_string(token)
    await repo.request_verification(email, token_hash)
    await email_backend.request_verification(email, token)
