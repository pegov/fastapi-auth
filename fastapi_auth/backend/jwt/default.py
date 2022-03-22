from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from fastapi_auth.backend.abc.jwt import AbstractJWTBackend
from fastapi_auth.errors import TokenDecodingError


class JWTBackend(AbstractJWTBackend):
    def __init__(
        self,
        algorithm: str = "EdDSA",
        private_key: Any = "",
        public_key: Any = "",
    ):
        self._algorithm = algorithm
        self._private_key = private_key
        self._public_key = public_key

    def create_token(
        self,
        type: str,
        payload: dict,
        expiration: int,
    ) -> str:
        iat = datetime.now(timezone.utc)
        exp = iat + timedelta(seconds=expiration)

        payload.update(
            {
                "type": type,
                "iat": iat,
                "exp": exp,
            }
        )

        return jwt.encode(payload, self._private_key, algorithm=self._algorithm)

    def decode_token(self, token: str) -> dict:
        if token:
            try:
                payload = jwt.decode(
                    token,
                    self._public_key,
                    algorithms=[self._algorithm],
                )
                return payload
            except Exception:
                pass

        raise TokenDecodingError
