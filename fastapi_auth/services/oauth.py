import asyncio
import random
from datetime import datetime, timezone
from typing import Iterable, Optional

from fastapi_auth.backend.abc.oauth import AbstractOAuthProvider
from fastapi_auth.errors import (
    EmailAlreadyExistsError,
    OAuthLoginOnlyError,
    UserNotActiveError,
    UserNotFoundError,
    WrongTokenTypeError,
)
from fastapi_auth.jwt import JWT, TokenParams
from fastapi_auth.models.oauth import OAuthAccountActionTokenPayload
from fastapi_auth.models.user import UserCreate, UserDB, UserUpdate
from fastapi_auth.repo import Repo

MAX_ATTEMPTS = 15


class OAuthService:
    def __init__(
        self,
        jwt: JWT,
        token_params: TokenParams,
        oauth_providers: Iterable[AbstractOAuthProvider],
        origin: str,
        path_prefix: str,
    ) -> None:
        self._jwt = jwt
        self._tp = token_params
        self._oauth_providers = oauth_providers
        self._origin = origin
        self._path_prefix = path_prefix

    def get_provider(self, provider_name: str) -> Optional[AbstractOAuthProvider]:
        for provider in self._oauth_providers:
            if provider.name == provider_name:
                return provider

        return None

    def create_redirect_uri(self, provider_name: str) -> str:
        return f"{self._origin}{self._path_prefix}/{provider_name}/callback"

    async def get_user(
        self,
        repo: Repo,
        provider: AbstractOAuthProvider,
        sid: str,
    ) -> Optional[UserDB]:
        try:
            item = await repo.get_by_provider_and_sid(provider.name, sid)
        except UserNotFoundError:  # pragma: no cover
            return None

        if not item.active:
            raise UserNotActiveError

        last_login_update_obj = UserUpdate(last_login=datetime.now(timezone.utc))
        asyncio.create_task(
            repo.update(
                item.id,
                last_login_update_obj.to_update_dict(),
            )
        )

        return item

    async def create_user(
        self,
        repo: Repo,
        provider: AbstractOAuthProvider,
        sid: str,
        email: str,
    ) -> UserDB:
        if provider.is_login_only():
            raise OAuthLoginOnlyError

        try:
            await repo.get_by_email(email)
            raise EmailAlreadyExistsError
        except UserNotFoundError:
            pass

        username = await self._resolve_username(repo, email)

        user_create = UserCreate(
            email=email,
            username=username,
            verified=True,
        )
        id = await repo.create(user_create)
        await repo.oauth.create(id, provider.name, sid)

        return await repo.get(id)

    async def _resolve_username(self, repo: Repo, email: str) -> str:
        username = email.split("@")[0]

        i = 0
        while True:
            postfix = str(i) if i > 0 else ""
            resolved_username = f"{username}{postfix}"
            try:
                await repo.get_by_username(resolved_username)
            except UserNotFoundError:
                return resolved_username

            i += 1  # pragma: no cover

            if i > MAX_ATTEMPTS:  # pragma: no cover
                postfix = "".join(random.choices("0123456789", k=6))
                resolved_username = f"{username}{postfix}"
                try:
                    await repo.get_by_username(resolved_username)
                    raise Exception("something is wrong")
                except UserNotFoundError:
                    return resolved_username

    async def add_oauth_account(
        self,
        repo: Repo,
        token: str,
        provider: str,
        sid: str,
    ) -> None:
        payload = self._jwt.decode_token(token)
        obj = OAuthAccountActionTokenPayload(**payload)

        if obj.type != self._tp.add_oauth_account_token_type:
            raise WrongTokenTypeError

        await repo.oauth.update(obj.id, provider, sid)
