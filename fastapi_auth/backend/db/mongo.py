import asyncio
from typing import Optional, Type

from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorCollection,
    AsyncIOMotorDatabase,
)
from pymongo import ReturnDocument

from fastapi_auth.backend.abc.db import AbstractDatabaseClient
from fastapi_auth.errors import UserNotFoundError
from fastapi_auth.models.user import UserDB
from fastapi_auth.types import UID


class MongoClient(AbstractDatabaseClient):
    def __init__(
        self,
        client: Optional[AsyncIOMotorClient],
        database_name: str,
        db_model: Type[UserDB],
    ) -> None:
        self._database_name = database_name
        if client is not None:
            self.set_client(client)

        self._db_model = db_model

        self._lock = asyncio.Lock()

    def set_client(self, client: AsyncIOMotorClient) -> None:
        self._client = client
        self._db: AsyncIOMotorDatabase = client[self._database_name]
        self._users: AsyncIOMotorCollection = self._db["users"]
        self._email_verifications: AsyncIOMotorCollection = self._db[
            "users.verifications"
        ]
        self._counters: AsyncIOMotorCollection = self._db["counters"]

    async def _increment_id(self) -> int:
        res = await self._counters.find_one_and_update(
            {"name": "users"},
            {"$inc": {"c": 1}},
            return_document=ReturnDocument.AFTER,
        )
        return res.get("c")

    async def _get(
        self,
        obj: dict,
    ) -> UserDB:
        item = await self._users.find_one(obj, {"_id": 0})
        if item is not None:
            return self._db_model(**item)

        raise UserNotFoundError

    async def get(self, id: UID) -> UserDB:
        return await self._get({"id": id})

    async def get_by_email(self, email: str) -> UserDB:
        return await self._get({"email": email})

    async def get_by_username(self, username: str) -> UserDB:
        return await self._get({"username": username})

    async def get_by_oauth(self, provider: str, sid: str) -> UserDB:
        return await self._get({"oauth.provider": provider, "oauth.sid": sid})

    async def create(self, obj: dict) -> UID:
        async with self._lock:
            id = await self._increment_id()
            obj.update({"id": id})
            await self._users.insert_one(obj)
        return id

    async def update(self, id: UID, obj: dict) -> bool:
        res = await self._users.update_one(
            {"id": id},
            {"$set": obj},
        )
        return bool(res.matched_count)

    async def delete(self, id: UID) -> bool:
        res = await self._users.delete_one({"id": id})
        return bool(res.deleted_count)
