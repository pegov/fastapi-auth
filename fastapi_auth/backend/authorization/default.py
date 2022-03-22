import asyncio

from fastapi_auth.backend.abc.authorization import AbstractAuthorization
from fastapi_auth.errors import AuthorizationError, WrongTokenTypeError
from fastapi_auth.models.user import User
from fastapi_auth.repo import Repo


class DefaultAuthorization(AbstractAuthorization):
    async def authorize(self, repo: Repo, user: User, token_type: str) -> None:

        if user.type != token_type:
            raise WrongTokenTypeError

        kick, ban, mass_logout = await asyncio.gather(
            repo.user_was_kicked(user.id, user.iat),
            repo.user_was_recently_banned(user.id),
            repo.user_in_mass_logout(user.iat),
        )

        if kick or ban or mass_logout:
            raise AuthorizationError
