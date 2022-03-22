import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from fastapi_auth import User

pytestmark = pytest.mark.asyncio


async def test_get_status(
    app: FastAPI,
    test_client: AsyncClient,
    mock_user: User,
):
    url = app.url_path_for("verify:get_status")
    res = await test_client.get(url)

    assert res.status_code == 200


async def test_request(
    app: FastAPI,
    test_client: AsyncClient,
    mock_unverified_user: User,
):
    url = app.url_path_for("verify:request")
    res = await test_client.post(url)

    assert res.status_code == 200


async def test_check(
    app: FastAPI,
    test_client: AsyncClient,
    mock_unverified_user: User,
):
    url = app.url_path_for("verify:check", token="verify")
    res = await test_client.post(url)

    assert res.status_code == 200
