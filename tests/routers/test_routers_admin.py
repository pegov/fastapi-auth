import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from fastapi_auth import User

pytestmark = pytest.mark.asyncio


async def test_get_mass_logout_status(
    app: FastAPI,
    test_client: AsyncClient,
    mock_admin: User,
):
    url = app.url_path_for("admin:get_mass_logout_status")
    res = await test_client.get(url)

    assert res.status_code == 200


async def test_activate_mass_logout(
    app: FastAPI,
    test_client: AsyncClient,
    mock_admin: User,
):
    url = app.url_path_for("admin:activate_mass_logout")
    res = await test_client.post(url)

    assert res.status_code == 200


async def test_deactivate_mass_logout(
    app: FastAPI,
    test_client: AsyncClient,
    mock_admin: User,
):
    url = app.url_path_for("admin:deactivate_mass_logout")
    res = await test_client.delete(url)

    assert res.status_code == 200


async def test_ban(
    app: FastAPI,
    test_client: AsyncClient,
    mock_admin: User,
):
    url = app.url_path_for("admin:ban", id="2")
    res = await test_client.post(url)

    assert res.status_code == 200


async def test_unban(
    app: FastAPI,
    test_client: AsyncClient,
    mock_admin: User,
):
    url = app.url_path_for("admin:unban", id="2")
    res = await test_client.post(url)

    assert res.status_code == 200


async def test_kick(
    app: FastAPI,
    test_client: AsyncClient,
    mock_admin: User,
):
    url = app.url_path_for("admin:kick", id="2")
    res = await test_client.post(url)

    assert res.status_code == 200


async def test_unkick(
    app: FastAPI,
    test_client: AsyncClient,
    mock_admin: User,
):
    url = app.url_path_for("admin:unkick", id="2")
    res = await test_client.post(url)

    assert res.status_code == 200
