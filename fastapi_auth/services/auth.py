import asyncio
from typing import Callable, Optional, Type

from fastapi_auth.backend.email.base import BaseEmailBackend
from fastapi_auth.models.auth import BaseUserTokenPayload, UserCreate, UserRegister
from fastapi_auth.repo import AuthRepo
from fastapi_auth.utils.password import get_password_hash
from fastapi_auth.utils.string import create_random_string, hash_string


async def create(
    repo: AuthRepo,
    user_in: UserRegister,
    hook: Optional[Callable[[dict], None]],
    user_token_payload_model: Type[BaseUserTokenPayload],
) -> BaseUserTokenPayload:
    password_hash = get_password_hash(user_in.password1)
    user_create = UserCreate(**user_in.dict(), password=password_hash)
    id = await repo.create(user_create.dict())
    if hook is not None:
        user = user_create.dict()
        user.update({"id": id})
        if asyncio.iscoroutinefunction(hook):
            await hook(user)  # type: ignore
        else:
            hook(user)
    return user_token_payload_model(id=id, **user_create.dict())


async def request_verification(
    repo: AuthRepo, email_backend: BaseEmailBackend, email: str
) -> None:
    token = create_random_string()
    token_hash = hash_string(token)
    await repo.request_verification(email, token_hash)
    await email_backend.request_verification(email, token)
