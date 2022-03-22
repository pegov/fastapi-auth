import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from fastapi_auth import User

pytestmark = pytest.mark.asyncio


async def test_get(
    app: FastAPI,
    test_client: AsyncClient,
    mock_user: User,
):
    url = app.url_path_for("me:get")
    res = await test_client.get(url)

    assert res.status_code == 200


async def test_change_username(
    app: FastAPI,
    test_client: AsyncClient,
    mock_user: User,
):
    url = app.url_path_for("me:change_username")
    data_in = {"username": "newusername"}
    res = await test_client.post(url, json=data_in)

    assert res.status_code == 200


async def test_request_email_change(
    app: FastAPI,
    test_client: AsyncClient,
    mock_user: User,
):
    url = app.url_path_for("me:request_email_change")
    data_in = {"email": "newemail@gmail.com"}
    res = await test_client.post(url, json=data_in)

    assert res.status_code == 200


async def test_check_old_email(
    app: FastAPI,
    test_client: AsyncClient,
):
    url = app.url_path_for("me:check_old_email", token="check_old_email")
    res = await test_client.post(url)

    assert res.status_code == 200


async def test_check_new_email(
    app: FastAPI,
    test_client: AsyncClient,
):
    url = app.url_path_for("me:check_new_email", token="check_new_email")
    res = await test_client.post(url)

    assert res.status_code == 200
