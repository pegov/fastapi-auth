from typing import Optional

from fastapi import Cookie, HTTPException

from fastapi_auth.core.jwt import JWTBackend


class User:
    def __init__(self, data=None):
        self.data = data
        if data is None:
            self.is_authenticated = False
            self.is_admin = False
            self.id = None
            self.username = None
        else:
            self.is_authenticated = True
            self.is_admin = "admin" in self.data.get("permissions")
            self.id = int(self.data.get("id"))
            self.username = self.data.get("username")

    @classmethod
    async def create(cls, token: str, backend):
        data = await backend.decode_token(token)
        return cls(data)


# TODO: BAD CODE, fix it later
async def get_user(access_c: Optional[str] = Cookie(None)) -> User:
    if access_c:
        return await User.create(access_c, JWTBackend())
    else:
        return User()


async def get_authenticated_user(
    access_c: Optional[str] = Cookie(None),
) -> User:
    if access_c:
        return await User.create(access_c, JWTBackend())
    else:
        raise HTTPException(401)


async def admin_required(access_c: Optional[str] = Cookie(None)) -> None:
    if access_c:
        user = await User.create(access_c, JWTBackend())
        if user.is_admin:
            return

    raise HTTPException(403)


# get_auhtenticated_user
