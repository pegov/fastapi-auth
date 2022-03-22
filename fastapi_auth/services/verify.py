from uuid import UUID

from fastapi_auth.backend.abc.email import AbstractEmailClient
from fastapi_auth.errors import (
    EmailAlreadyVerifiedError,
    EmailMismatchError,
    TimeoutError,
    WrongTokenTypeError,
)
from fastapi_auth.jwt import JWT, TokenParams
from fastapi_auth.models.user import User, UserUpdate
from fastapi_auth.models.verify import VerificationPayload, VerificationStatusResponse
from fastapi_auth.repo import Repo
from fastapi_auth.types import UID


async def request_verification(
    jwt: JWT,
    tp: TokenParams,
    email_client: AbstractEmailClient,
    id: UID,
    email: str,
) -> None:
    payload = {
        "id": str(id) if isinstance(id, UUID) else id,
        "email": email,
    }
    token = jwt.create_token(
        tp.verify_email_token_type,
        payload,
        tp.verify_email_token_expiration,
    )
    await email_client.request_verification(email, token)


class VerifyService:
    def __init__(
        self,
        repo: Repo,
        jwt: JWT,
        token_params: TokenParams,
        email_client: AbstractEmailClient,
    ) -> None:
        self._repo = repo
        self._jwt = jwt
        self._tp = token_params
        self._email_client = email_client

    async def get_status(self, user: User) -> VerificationStatusResponse:
        item = await self._repo.get(user.id)
        return VerificationStatusResponse(**item.dict())

    async def request(self, user: User) -> None:
        item = await self._repo.get(user.id)

        if item.verified:
            raise EmailAlreadyVerifiedError

        if await self._repo.rate_limit_reached(
            self._tp.verify_email_token_type,
            2,
            60 * 60,
            60 * 30,
            user.id,
        ):
            raise TimeoutError

        await request_verification(
            self._jwt,
            self._tp,
            self._email_client,
            user.id,
            item.email,
        )

    async def verify(self, token: str) -> None:
        payload = self._jwt.decode_token(token)
        data = VerificationPayload(**payload)

        if data.type != self._tp.verify_email_token_type:
            raise WrongTokenTypeError

        user = await self._repo.get(data.id)

        if user.verified:
            raise EmailAlreadyVerifiedError

        if user.email != data.email:
            raise EmailMismatchError

        await self._repo.use_token(token, ex=self._tp.verify_email_token_expiration)

        update_obj = UserUpdate(verified=True)
        await self._repo.update(user.id, update_obj.to_update_dict())
