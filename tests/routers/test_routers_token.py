import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from fastapi_auth.models.user import User

pytestmark = pytest.mark.asyncio


async def test_token(
    app: FastAPI,
    test_client: AsyncClient,
    mock_user: User,
):
    url = app.url_path_for("token:payload")
    res = await test_client.post(url)

    assert res.status_code == 200


async def test_refresh_access_token(
    app: FastAPI,
    test_client: AsyncClient,
):
    url = app.url_path_for("token:refresh_access_token")
    res = await test_client.post(url)

    assert res.status_code == 200
