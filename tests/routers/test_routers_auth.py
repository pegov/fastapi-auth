import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from fastapi_auth import User

pytestmark = pytest.mark.asyncio


async def test_register(
    app: FastAPI,
    test_client: AsyncClient,
):
    url = app.url_path_for("auth:register")
    data_in = {
        "email": "newemail@gmail.com",
        "username": "newusername",
        "password1": "123456",
        "password2": "123456",
        "captcha": "value",
    }
    res = await test_client.post(url, json=data_in)

    assert res.status_code == 200


async def test_login(
    app: FastAPI,
    test_client: AsyncClient,
):
    url = app.url_path_for("auth:login")
    data_in = {
        "login": "admin",
        "password": "123456",
    }
    res = await test_client.post(url, json=data_in)

    assert res.status_code == 200


async def test_logout(
    app: FastAPI,
    test_client: AsyncClient,
):
    url = app.url_path_for("auth:logout")
    res = await test_client.post(url)

    assert res.status_code == 200


async def test_token(
    app: FastAPI,
    test_client: AsyncClient,
    mock_user: User,
):
    url = app.url_path_for("auth:token")
    res = await test_client.post(url)

    assert res.status_code == 200


async def test_refresh_access_token(
    app: FastAPI,
    test_client: AsyncClient,
):
    url = app.url_path_for("auth:refresh_access_token")
    res = await test_client.post(url)

    assert res.status_code == 200
