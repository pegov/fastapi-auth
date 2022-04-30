import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from fastapi_auth import User

pytestmark = pytest.mark.asyncio


async def test_request_verification(
    app: FastAPI,
    test_client: AsyncClient,
    mock_unverified_user: User,
):
    url = app.url_path_for("email:request_verification")
    res = await test_client.post(url)

    assert res.status_code == 200


async def test_verify(
    app: FastAPI,
    test_client: AsyncClient,
    mock_unverified_user: User,
):
    url = app.url_path_for("email:verify", token="verify")
    res = await test_client.post(url)

    assert res.status_code == 200


async def test_request_email_change(
    app: FastAPI,
    test_client: AsyncClient,
    mock_user: User,
):
    url = app.url_path_for("email:request_email_change")
    data_in = {"email": "newemail@gmail.com"}
    res = await test_client.post(url, json=data_in)

    assert res.status_code == 200


async def test_verify_old(
    app: FastAPI,
    test_client: AsyncClient,
):
    url = app.url_path_for("email:verify_old", token="verify_old_email")
    res = await test_client.post(url)

    assert res.status_code == 200


async def test_verify_new(
    app: FastAPI,
    test_client: AsyncClient,
):
    url = app.url_path_for("email:verify_new", token="verify_new_email")
    res = await test_client.post(url)

    assert res.status_code == 200
