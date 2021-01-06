from datetime import datetime, timedelta
from typing import Optional

import jwt

from fastapi_auth.db.backend import RedisBackend


class JWTBackend:
    _cache: Optional[RedisBackend] = None
    _jwt_algorithm: str
    _private_key: bytes
    _public_key: bytes
    _access_expiration: int
    _refresh_expiration: int

    @classmethod
    def create(
        cls,
        jwt_algorithm: str,
        private_key: bytes,
        public_key: bytes,
        access_expiration: int,
        refresh_expiration: int,
    ) -> None:
        cls._jwt_algorithm = jwt_algorithm
        cls._private_key = private_key
        cls._public_key = public_key
        cls._access_expiration = access_expiration
        cls._refresh_expiration = refresh_expiration

    @classmethod
    def set_cache(cls, cache: RedisBackend) -> None:
        cls._cache = cache

    async def _active_blackout_exists(self, iat: datetime) -> bool:
        blackout = await self._cache.get("users:blackout")
        if blackout is not None:
            blackout_ts = datetime.utcfromtimestamp(int(blackout))
            return blackout_ts >= iat
        else:
            return False

    async def _user_in_blacklist(self, id: int) -> bool:
        in_blacklist = await self._cache.get(f"users:blacklist:{id}")
        return bool(in_blacklist)

    async def _user_in_logout(self, id: int, iat: datetime) -> bool:
        ts = await self._cache.get(f"users:kick:{id}")
        if ts is not None:
            logout_ts = datetime.utcfromtimestamp(int(ts))
            return logout_ts >= iat
        else:
            return False

    async def decode_token(self, token: str, leeway: int = 0) -> Optional[dict]:
        if token:
            try:
                payload = jwt.decode(
                    token,
                    self._public_key,
                    leeway=leeway,
                    algorithms=self._jwt_algorithm,
                )
                id = payload.get("id")
                iat = datetime.utcfromtimestamp(int(payload.get("iat")))
                active_blackout_exists = await self._active_blackout_exists(iat)
                user_in_blacklist = await self._user_in_blacklist(id)
                user_in_logout = await self._user_in_logout(id, iat)
                if active_blackout_exists or user_in_blacklist or user_in_logout:
                    return None

                return payload
            except:  # noqa E722
                return None
        return None

    def _create_token(
        self, payload: dict, token_type: str, expiration_delta: Optional[int] = None
    ) -> str:
        iat = datetime.utcnow()
        if expiration_delta:
            exp = datetime.utcnow() + timedelta(seconds=expiration_delta)
        else:
            exp = datetime.utcnow() + timedelta(seconds=60)

        payload.update({"iat": iat, "exp": exp, "type": token_type})

        return jwt.encode(
            payload, self._private_key, algorithm=self._jwt_algorithm
        ).decode()

    def create_access_token(self, payload: dict) -> str:
        return self._create_token(payload, "access", self._access_expiration)

    def create_refresh_token(self, payload: dict) -> str:
        return self._create_token(payload, "refresh", self._refresh_expiration)

    def create_tokens(self, payload: dict) -> dict:
        access = self.create_access_token(payload)
        refresh = self.create_refresh_token(payload)

        return {"access": access, "refresh": refresh}
