from typing import Tuple

from httpx import AsyncClient

from .base import BaseOAuthProvider


class VKOAuthProvider(BaseOAuthProvider):
    name: str = "vk"

    def create_oauth_uri(self, redirect_uri: str, state: str) -> str:
        return (
            f"https://oauth.vk.com/authorize"
            f"?client_id={self._id}"
            "&scope=email"
            f"&redirect_uri={redirect_uri}"
            "&response_type=code"
            "&v=5.122"
            f"&state={state}"
        )

    async def get_user_data(self, redirect_uri: str, code: str) -> Tuple[str, str]:
        async with AsyncClient(base_url="https://oauth.vk.com") as client:
            response = await client.get(
                "/access_token",
                params={
                    "client_id": self._id,
                    "client_secret": self._secret,
                    "code": code,
                    "redirect_uri": redirect_uri,
                },
            )

        data = response.json()
        sid = data.get("user_id")
        email = data.get("email")

        return str(sid), email
