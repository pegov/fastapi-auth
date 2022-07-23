from fastapi_auth.backend.abc.email import AbstractEmailClient
from fastapi_auth.errors import (
    EmailAlreadyVerifiedError,
    EmailMismatchError,
    SameEmailError,
    TimeoutError,
    WrongTokenTypeError,
)
from fastapi_auth.jwt import JWT, TokenParams
from fastapi_auth.models.email import ChangeEmailRequest, EmailActionTokenPayload
from fastapi_auth.models.user import User, UserUpdate
from fastapi_auth.repo import Repo


async def request_verification(
    jwt: JWT,
    tp: TokenParams,
    email_client: AbstractEmailClient,
    id: int,
    email: str,
) -> None:
    payload = {
        "id": id,
        "email": email,
    }
    token = jwt.create_token(
        tp.verify_email_token_type,
        payload,
        tp.verify_email_token_expiration,
    )
    await email_client.request_verification(email, token)


class EmailService:
    def __init__(
        self,
        jwt: JWT,
        token_params: TokenParams,
        email_client: AbstractEmailClient,
    ) -> None:
        self._jwt = jwt
        self._tp = token_params
        self._email_client = email_client

    async def request_verification(self, repo: Repo, user: User) -> None:
        item = await repo.get(user.id)

        if item.verified:
            raise EmailAlreadyVerifiedError

        if await repo.rate_limit_reached(
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

    async def verify(self, repo: Repo, token: str) -> None:
        payload = self._jwt.decode_token(token)
        data = EmailActionTokenPayload(**payload)

        if data.type != self._tp.verify_email_token_type:
            raise WrongTokenTypeError

        user = await repo.get(data.id)

        if user.verified:
            raise EmailAlreadyVerifiedError

        if user.email != data.email:
            raise EmailMismatchError

        await repo.use_token(token, ex=self._tp.verify_email_token_expiration)

        update_obj = UserUpdate(verified=True)
        await repo.update(user.id, update_obj.to_update_dict())

    async def request_email_change(
        self,
        repo: Repo,
        data_in: ChangeEmailRequest,
        user: User,
    ) -> None:
        item = await repo.get(user.id)

        if data_in.email == item.email:
            raise SameEmailError

        if await repo.rate_limit_reached(
            "request_email_change",
            2,
            60 * 30,
            60 * 60,
            user.id,
        ):
            raise TimeoutError

        payload = {
            "id": user.id,
            "email": data_in.email,
        }
        token = self._jwt.create_token(
            self._tp.check_old_email_token_type,
            payload,
            self._tp.change_email_token_expiration,
        )
        await self._email_client.check_old_email(item.email, token)

    async def verify_old(self, repo: Repo, token: str) -> None:
        payload = self._jwt.decode_token(token)
        obj = EmailActionTokenPayload(**payload)

        if obj.type != self._tp.check_old_email_token_type:  # pragma: no cover
            raise WrongTokenTypeError

        await repo.use_token(token, self._tp.change_email_token_expiration)

        token = self._jwt.create_token(
            self._tp.check_new_email_token_type,
            payload,
            self._tp.change_email_token_expiration,
        )

        await self._email_client.check_new_email(obj.email, token)

    async def verify_new(self, repo: Repo, token: str) -> None:
        payload = self._jwt.decode_token(token)
        obj = EmailActionTokenPayload(**payload)

        if obj.type != self._tp.check_new_email_token_type:  # pragma: no cover
            raise WrongTokenTypeError

        await repo.use_token(token, self._tp.change_email_token_expiration)

        update_obj = UserUpdate(email=obj.email)
        await repo.update(obj.id, update_obj.to_update_dict())
