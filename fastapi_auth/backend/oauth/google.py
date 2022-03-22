from typing import Tuple

import jwt
from httpx import AsyncClient

from .base import BaseOAuthProvider


class GoogleOAuthProvider(BaseOAuthProvider):
    name: str = "google"

    def create_oauth_uri(self, redirect_uri: str, state: str) -> str:
        return (
            f"https://accounts.google.com/o/oauth2/v2/auth"
            "?scope=email%20profile"
            "&response_type=code"
            f"&state={state}"
            f"&redirect_uri={redirect_uri}"
            f"&client_id={self._id}"
        )

    async def get_user_data(self, redirect_uri: str, code: str) -> Tuple[str, str]:
        async with AsyncClient(base_url="https://oauth2.googleapis.com") as client:
            response = await client.post(
                "/token",
                params={
                    "client_id": self._id,
                    "client_secret": self._secret,
                    "code": code,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
            )

        data = response.json()
        id_token = data.get("id_token")
        payload = jwt.decode(id_token, options={"verify_signature": False})
        sid = payload.get("sub")
        email = payload.get("email")

        return str(sid), email
