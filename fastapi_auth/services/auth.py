import asyncio
from typing import Callable, Optional, Type

from fastapi_auth.backend.email.base import BaseEmailBackend
from fastapi_auth.models.auth import BaseUserCreate, BaseUserTokenPayload, UserRegister
from fastapi_auth.repo import AuthRepo
from fastapi_auth.utils.password import get_password_hash
from fastapi_auth.utils.string import create_random_string, hash_string


async def create(
    repo: AuthRepo,
    user_in: UserRegister,
    user_create_model: Type[BaseUserCreate],
    hook: Optional[Callable[[dict], None]],
    user_token_payload_model: Type[BaseUserTokenPayload],
) -> BaseUserTokenPayload:
    password_hash = get_password_hash(user_in.password1)
    user_create = user_create_model(**user_in.dict(), password=password_hash)
    id = await repo.create(user_create.dict())
    if hook is not None:
        user = user_create.dict()
        user.update({"id": id})
        if asyncio.iscoroutinefunction(hook):
            await hook(user)  # type: ignore
        else:
            hook(user)
    return user_token_payload_model(id=id, **user_create.dict())


async def request_email_confirmation(
    repo: AuthRepo, email_backend: BaseEmailBackend, email: str
) -> None:
    token = create_random_string()
    token_hash = hash_string(token)
    await repo.request_email_confirmation(email, token_hash)
    await email_backend.send_confirmation_email(email, token)
