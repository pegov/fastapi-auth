from pathlib import Path
from typing import List, Optional

from asyncpg import Connection
from sqlsl import Queries

from fastapi_auth.backend.abc.db import (
    AbstractDatabaseClient,
    AbstractDatabaseOAuthExtension,
    AbstractDatabaseRolesExtension,
)
from fastapi_auth.errors import RoleNotFoundError
from fastapi_auth.models.user import OAuthDB, RoleDB, UserCreate, UserDB


class Q(Queries):
    create_user: str
    get_user_by_id: str
    get_user_by_username: str
    get_user_by_email: str
    get_user_by_provider_and_sid: str
    update_user_by_id: str
    delete_user_by_id: str

    create_oauth: str
    get_oauth_by_user_id: str
    get_oauth_by_provider_and_sid: str
    update_oauth_by_id: str
    update_oauth_by_user_id: str
    delete_oauth_by_id: str
    delete_oauth_by_user_id: str

    get_all_roles_and_permissions: str

    create_role: str
    get_role_by_name: str
    get_role_and_permissions_by_name: str
    delete_role_by_name: str

    grant_role_by_name: str
    revoke_role_by_name: str

    create_permission: str
    get_permission_by_name: str

    get_user_role_relation: str
    create_user_role_relation: str
    delete_user_role_relation: str

    get_role_permission_relation: str
    create_role_permission_relation: str
    delete_role_permission_relation: str


path = Path(__file__).parent / "postgres_sql"
q = Q().from_dir(path)


class PostgresOAuthExtension(AbstractDatabaseOAuthExtension):
    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    def _create_obj(self, oauth: Optional[dict]) -> Optional[OAuthDB]:
        if oauth is not None:
            return OAuthDB(
                user_id=oauth.get("user_id"),  # type: ignore
                provider=oauth.get("provider"),  # type: ignore
                sid=oauth.get("sid"),  # type: ignore
            )

        return None

    async def get_by_user_id(self, user_id: int) -> Optional[OAuthDB]:
        oauth = await self._conn.fetchrow(q.get_oauth_by_user_id, user_id)
        return self._create_obj(oauth)

    # not in ABC
    async def get_by_provider_and_sid(
        self,
        provider: str,
        sid: str,
    ) -> Optional[OAuthDB]:
        return await self._conn.fetchrow(q.get_oauth_by_provider_and_sid, provider, sid)

    async def create(self, user_id: int, provider: str, sid: str) -> None:
        await self._conn.execute(
            q.create_oauth,
            user_id,
            provider,
            sid,
        )

    async def update_by_user_id(self, user_id: int, provider: str, sid: str) -> None:
        await self._conn.execute(
            q.update_oauth_by_user_id,
            user_id,
            provider,
            sid,
        )

    async def delete_by_user_id(self, user_id: int) -> None:
        await self._conn.execute(q.delete_oauth_by_user_id, user_id)


class PostgresRolesExtension(AbstractDatabaseRolesExtension):
    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    async def create(self, name: str) -> int:
        role = await self.get_by_name(name)
        if role is not None:
            return role.get("id")  # type: ignore

        res = await self._conn.fetchval(q.create_role, name)
        return res  # type: ignore

    async def get_by_name(self, name: str) -> Optional[RoleDB]:
        role = await self._conn.fetchrow(q.get_role_and_permissions_by_name, name)  # type: ignore
        if role is not None:
            return RoleDB(**role)  # type: ignore

        return None

    async def add_permission(self, role_name: str, permission_name: str) -> None:
        async with self._conn.transaction():
            role_id = await self._conn.fetchval(q.get_role_by_name, role_name)
            if role_id is None:
                raise RoleNotFoundError

            permission_id = await self._conn.fetchval(
                q.get_permission_by_name,
                permission_name,
            )
            if permission_id is None:
                permission_id = await self._conn.fetchval(
                    q.create_permission,
                    permission_name,
                )

            if (
                await self._conn.fetchrow(
                    q.get_role_permission_relation,
                    role_id,
                    permission_id,
                )
                is not None
            ):
                return

            await self._conn.execute(
                q.create_role_permission_relation,
                role_id,
                permission_id,
            )

    async def remove_permission(self, role_name: str, permission_name: str) -> None:
        async with self._conn.transaction():
            role_id = await self._conn.fetchval(q.get_role_by_name, role_name)
            permission_id = await self._conn.fetchval(
                q.get_permission_by_name, permission_name
            )
            if role_id is None or permission_id is None:
                raise RoleNotFoundError

            await self._conn.execute(
                q.delete_role_permission_relation,
                role_id,
                permission_id,
            )

    async def delete_by_name(self, name: str) -> None:
        await self._conn.execute(q.delete_role_by_name, name)

    async def _get_role_id(self, role_name: str) -> int:
        role_id = await self._conn.fetchval(q.get_role_by_name, role_name)
        if role_id is None:
            raise RoleNotFoundError

        return role_id  # type: ignore

    async def grant(self, user_id: int, role_name: str) -> None:
        async with self._conn.transaction():
            role_id = await self._get_role_id(role_name)

            await self._conn.execute(q.create_user_role_relation, user_id, role_id)

    async def revoke(self, user_id: int, role_name: str) -> None:
        async with self._conn.transaction():
            role_id = await self._get_role_id(role_name)

            await self._conn.execute(q.delete_user_role_relation, user_id, role_id)

    async def all(self) -> List[RoleDB]:
        roles = await self._conn.fetch(q.get_all_roles_and_permissions)
        return [RoleDB(**role) for role in roles]


class PostgresClient(AbstractDatabaseClient):
    def __init__(self, conn: Connection) -> None:
        self._conn = conn
        self.oauth = PostgresOAuthExtension(conn)
        self.roles = PostgresRolesExtension(conn)

    def _create_obj(self, user: Optional[dict]) -> Optional[UserDB]:
        if user is None:
            return None

        if user.get("oauth_provider") is not None:
            oauth = OAuthDB(
                user_id=user.get("id"),  # type: ignore
                provider=user.get("oauth_provider"),  # type: ignore
                sid=user.get("oauth_sid"),  # type: ignore
            )
        else:
            oauth = None

        return UserDB(**user, oauth=oauth)

    async def get_by_id(self, id: int) -> Optional[UserDB]:
        return await self._conn.fetchrow(q.get_user_by_id, id)  # type: ignore

    async def get_by_email(self, email: str) -> Optional[UserDB]:
        return await self._conn.fetchrow(q.get_user_by_email, email)  # type: ignore

    async def get_by_username(self, username: str) -> Optional[UserDB]:
        return await self._conn.fetchrow(q.get_user_by_username, username)  # type: ignore

    async def get_by_provider_and_sid(
        self, provider: str, sid: str
    ) -> Optional[UserDB]:
        return await self._conn.fetchrow(
            q.get_user_by_provider_and_sid, provider, sid  # type: ignore
        )

    async def create(self, obj: UserCreate) -> int:
        return await self._conn.fetchval(q.create_user, *obj.dict().values())  # type: ignore

    async def update_by_id(self, id: int, obj: dict) -> bool:
        if await self._conn.fetchrow(q.get_user_by_id, id) is None:
            return False

        async with self._conn.transaction():
            for key, value in obj.items():
                value = await self._conn.execute(q.update_user_by_id, id, key, value)

        return True

    async def delete_by_id(self, id: int) -> bool:
        if await self._conn.fetchrow(q.get_user_by_id, id) is None:
            return False

        await self._conn.execute(q.delete_user_by_id, id)

        return True
