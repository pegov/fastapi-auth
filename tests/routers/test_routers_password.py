import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from fastapi_auth import User

pytestmark = pytest.mark.asyncio


async def test_forgot(
    app: FastAPI,
    test_client: AsyncClient,
    mock_user: User,
):
    url = app.url_path_for("password:forgot")
    data_in = {"email": "example1@gmail.com", "captcha": "value"}
    res = await test_client.post(url, json=data_in)

    assert res.status_code == 200


async def test_get_status(
    app: FastAPI,
    test_client: AsyncClient,
    mock_user: User,
):
    url = app.url_path_for("password:get_status")
    res = await test_client.get(url)

    assert res.status_code == 200


async def test_set(
    app: FastAPI,
    test_client: AsyncClient,
    mock_social_user: User,
):
    url = app.url_path_for("password:set")
    data_in = {
        "password1": "123456",
        "password2": "123456",
    }
    res = await test_client.post(url, json=data_in)

    assert res.status_code == 200


async def test_change(
    app: FastAPI,
    test_client: AsyncClient,
    mock_user: User,
):
    url = app.url_path_for("password:change")
    data_in = {
        "old_password": "123456",
        "password1": "1234567",
        "password2": "1234567",
    }
    res = await test_client.post(url, json=data_in)

    assert res.status_code == 200


async def test_reset(
    app: FastAPI,
    test_client: AsyncClient,
):
    url = app.url_path_for("password:reset")
    data_in = {
        "token": "reset_password",
        "password1": "123456",
        "password2": "123456",
    }
    res = await test_client.post(url, json=data_in)

    assert res.status_code == 200
