import pytest
from fastapi import FastAPI
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_login(
    app: FastAPI,
    test_client: AsyncClient,
):
    url = app.url_path_for("oauth:login", provider_name="mock")
    res = await test_client.get(url)

    assert res.status_code == 307


# TODO
