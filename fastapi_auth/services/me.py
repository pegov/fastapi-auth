from typing import Tuple
from uuid import UUID

from fastapi_auth.backend.abc.email import AbstractEmailClient
from fastapi_auth.errors import (
    OAuthAccountAlreadyExistsError,
    OAuthAccountNotSetError,
    PasswordNotSetError,
    SameUsernameError,
    UsernameAlreadyExistsError,
    UserNotFoundError,
    WrongTokenTypeError,
)
from fastapi_auth.jwt import JWT, TokenParams
from fastapi_auth.models.me import ChangeUsernameRequest
from fastapi_auth.models.oauth import OAuthAccountActionTokenPayload
from fastapi_auth.models.user import User, UserDB, UserUpdate
from fastapi_auth.repo import Repo


class MeService:
    def __init__(
        self,
        repo: Repo,
        jwt: JWT,
        token_params: TokenParams,
        email_client: AbstractEmailClient,
    ):
        self._repo = repo
        self._authentication = jwt
        self._email_client = email_client
        self._tp = token_params

    async def get(self, user: User) -> UserDB:
        return await self._repo.get(user.id)

    async def change_username(
        self, data_in: ChangeUsernameRequest, user: User
    ) -> Tuple[User, UserUpdate]:
        item = await self._repo.get(user.id)

        if data_in.username == item.username:
            raise SameUsernameError

        try:
            await self._repo.get_by_username(data_in.username)
            raise UsernameAlreadyExistsError
        except UserNotFoundError:
            pass

        update_obj = UserUpdate(username=data_in.username)

        await self._repo.update(
            user.id,
            update_obj.to_update_dict(),
        )

        # NOTE: refresh access token on frontend

        return user, update_obj

    async def add_oauth_account(self, provider: str, user: User) -> str:
        item = await self._repo.get(user.id)

        if item.oauth is not None:
            raise OAuthAccountAlreadyExistsError

        payload = {
            "id": str(user.id) if isinstance(id, UUID) else user.id,
            "provider": provider,
        }

        return self._authentication.create_token(
            self._tp.add_oauth_account_token_type,
            payload,
            self._tp.add_oauth_account_token_expiration,
        )

    async def request_oauth_account_removal(self, user: User) -> None:
        item = await self._repo.get(user.id)

        if item.oauth is None:
            raise OAuthAccountNotSetError

        if item.password is None:
            raise PasswordNotSetError

        payload = {
            "id": str(user.id) if isinstance(id, UUID) else user.id,
        }
        token = self._authentication.create_token(
            self._tp.remove_oauth_account_token_type,
            payload,
            self._tp.remove_oauth_account_token_expiration,
        )

        await self._email_client.request_oauth_account_removal(item.email, token)

    async def remove_oauth_account(self, token: str) -> None:
        payload = self._authentication.decode_token(token)
        obj = OAuthAccountActionTokenPayload(**payload)
        if obj.type != self._tp.remove_oauth_account_token_type:
            raise WrongTokenTypeError

        await self._repo.use_token(
            token, self._tp.remove_oauth_account_token_expiration
        )

        update_obj = UserUpdate()
        await self._repo.update(obj.id, update_obj.remove_oauth_account())
