from fastapi_auth.backend.abc.authorization import AbstractAuthorization
from fastapi_auth.errors import UserNotActiveError
from fastapi_auth.models.user import User, UserDB
from fastapi_auth.repo import Repo


class TokenService:
    def __init__(
        self,
        repo: Repo,
        authorization: AbstractAuthorization,
    ) -> None:
        self._repo = repo
        self._authorization = authorization

    async def authorize(self, user: User) -> UserDB:
        await self._authorization.authorize(self._repo, user, "refresh")
        user_db = await self._repo.get(user.id)
        if not user_db.active:
            raise UserNotActiveError

        return user_db
