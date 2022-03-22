from datetime import datetime, timezone

from fastapi_auth.backend.abc.db import AbstractDatabaseClient
from fastapi_auth.errors import UserNotFoundError
from fastapi_auth.models.user import UserDB
from fastapi_auth.types import UID


class MockDatabaseClient(AbstractDatabaseClient):
    def __init__(self) -> None:
        self.db: dict = {
            1: {
                "id": 1,
                "email": "example1@gmail.com",
                "username": "admin",
                "password": "123456",
                "roles": ["admin"],
                "active": True,
                "verified": True,
                "created_at": datetime.now(timezone.utc),
                "last_login": datetime.now(timezone.utc),
            },
            2: {
                "id": 2,
                "email": "example2@gmail.com",
                "username": "user",
                "password": "123456",
                "roles": [],
                "active": True,
                "verified": True,
                "created_at": datetime.now(timezone.utc),
                "last_login": datetime.now(timezone.utc),
            },
            3: {
                "id": 3,
                "email": "example3@gmail.com",
                "username": "social",
                "roles": [],
                "oauth": {
                    "provider": "mock",
                    "sid": "3",
                },
                "active": True,
                "verified": True,
                "created_at": datetime.now(timezone.utc),
                "last_login": datetime.now(timezone.utc),
            },
            4: {
                "id": 4,
                "email": "example4@gmail.com",
                "username": "unverified",
                "password": "123456",
                "roles": [],
                "active": True,
                "verified": False,
                "created_at": datetime.now(timezone.utc),
                "last_login": datetime.now(timezone.utc),
            },
            5: {
                "id": 5,
                "email": "example5@gmail.com",
                "username": "banned",
                "password": "123456",
                "oauth": {
                    "provider": "mock",
                    "sid": "5",
                },
                "roles": [],
                "active": False,
                "verified": False,
                "created_at": datetime.now(timezone.utc),
                "last_login": datetime.now(timezone.utc),
            },
            6: {
                "id": 6,
                "email": "example6@gmail.com",
                "username": "social_with_password",
                "password": "123456",
                "oauth": {
                    "provider": "mock",
                    "sid": "6",
                },
                "roles": [],
                "active": True,
                "verified": True,
                "created_at": datetime.now(timezone.utc),
                "last_login": datetime.now(timezone.utc),
            },
        }
        self.oauth = [
            {
                "user_id": 3,
                "provider": "mock",
                "sid": "3",
            },
            {
                "user_id": 5,
                "provider": "mock",
                "sid": "5",
            },
        ]
        self.i: int = 6

    async def get(self, id: UID) -> UserDB:
        v = self.db.get(id)
        if v is not None:
            return UserDB(**v)

        raise UserNotFoundError

    async def get_by_email(self, email: str) -> UserDB:
        for key, value in self.db.items():
            if value.get("email") == email:
                return await self.get(key)

        raise UserNotFoundError

    async def get_by_username(self, username: str) -> UserDB:
        for key, value in self.db.items():
            if value.get("username") == username:
                return await self.get(key)

        raise UserNotFoundError

    async def get_by_social(self, provider: str, sid: str) -> UserDB:
        for key, value in self.db.items():
            oauth = value.get("oauth")
            if oauth is not None:
                if value.get("provider") == provider and value.get("sid") == sid:
                    return await self.get(key)

        raise UserNotFoundError

    async def get_by_oauth(self, provider: str, sid: str) -> UserDB:
        for item in self.oauth:
            if item.get("provider") == provider and item.get("sid") == sid:
                return await self.get(item.get("user_id"))

        raise UserNotFoundError

    async def create(self, obj: dict) -> UID:
        self.i += 1
        obj.update({"id": self.i})
        self.db[self.i] = obj
        return self.i

    async def update(self, id: UID, obj: dict) -> bool:
        try:
            await self.get(id)
        except UserNotFoundError:
            return False

        self.db[id].update(obj)
        return True

    async def delete(self, id: UID) -> bool:
        try:
            await self.get(id)
        except UserNotFoundError:
            return False

        self.db.pop(id, None)
        return True
