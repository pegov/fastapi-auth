from typing import Tuple

from httpx import AsyncClient

from .base import BaseOAuthProvider


class FacebookOAuthProvider(BaseOAuthProvider):
    name: str = "facebook"

    def create_oauth_uri(self, redirect_uri: str, state: str) -> str:
        return (
            f"https://www.facebook.com/v8.0/dialog/oauth"
            f"?client_id={self._id}"
            f"&redirect_uri={redirect_uri}"
            f"&state={state}"
            "&scope=email"
        )

    async def get_user_data(self, redirect_uri: str, code: str) -> Tuple[str, str]:
        async with AsyncClient(base_url="https://graph.facebook.com") as client:
            response = await client.get(
                "/v8.0/oauth/access_token",
                params={
                    "client_id": self._id,
                    "client_secret": self._secret,
                    "code": code,
                    "redirect_uri": redirect_uri,
                },
            )

            data = response.json()
            access_token = data.get("access_token")

            response = await client.get(
                "/me",
                params={
                    "access_token": access_token,
                    "fields": "id,email",
                },
            )

        data = response.json()
        sid = data.get("user_id")
        email = data.get("email")

        return str(sid), email
