import asyncio
from typing import Iterable

import pytest
from fastapi import FastAPI, HTTPException
from httpx import AsyncClient
from starlette.middleware.sessions import SessionMiddleware

from fastapi_auth import FastAPIAuthApp
from fastapi_auth.backend.abc.authorization import AbstractAuthorization
from fastapi_auth.backend.abc.cache import AbstractCacheClient
from fastapi_auth.backend.abc.captcha import AbstractCaptchaClient
from fastapi_auth.backend.abc.db import AbstractDatabaseClient
from fastapi_auth.backend.abc.email import AbstractEmailClient
from fastapi_auth.backend.abc.jwt import AbstractJWTBackend
from fastapi_auth.backend.abc.oauth import AbstractOAuthProvider
from fastapi_auth.backend.abc.password import AbstractPasswordBackend
from fastapi_auth.backend.abc.transport import AbstractTransport
from fastapi_auth.backend.abc.validator import AbstractValidator
from fastapi_auth.dependencies import admin_required, get_authenticated_user, get_user
from fastapi_auth.jwt import TokenParams
from fastapi_auth.models.user import Anonim, User

pytest_plugins = ["backend_mocks"]


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def app(
    mock_db: AbstractDatabaseClient,
    mock_cache: AbstractCacheClient,
    mock_jwt_backend: AbstractJWTBackend,
    mock_transport: AbstractTransport,
    mock_authorization: AbstractAuthorization,
    mock_oauth_providers: Iterable[AbstractOAuthProvider],
    mock_password_backend: AbstractPasswordBackend,
    mock_email_client: AbstractEmailClient,
    mock_captcha_client: AbstractCaptchaClient,
    mock_validator: AbstractValidator,
):
    app = FastAPI()
    app.add_middleware(
        SessionMiddleware,
        secret_key="secret",
    )
    auth_app = FastAPIAuthApp(
        app,
        mock_db,
        mock_cache,
        mock_jwt_backend,
        TokenParams(),
        60,
        60,
        mock_transport,
        mock_authorization,
        mock_oauth_providers,
        mock_password_backend,
        mock_email_client,
        mock_captcha_client,
        validator=mock_validator,
    )

    app.include_router(auth_app.get_auth_router(), prefix="/api/users")
    app.include_router(auth_app.get_password_router(), prefix="/api/users")
    app.include_router(auth_app.get_me_router(), prefix="/api/users")
    app.include_router(auth_app.get_verify_router(), prefix="/api/users")
    app.include_router(auth_app.get_admin_router(), prefix="/api/users")
    app.include_router(auth_app.get_oauth_router(), prefix="/api/users")

    yield app


@pytest.fixture
async def test_client(app: FastAPI):
    async with AsyncClient(
        app=app,
        base_url="http://testserver",
        headers={"Content-Type": "application/json"},
    ) as client:
        yield client


@pytest.fixture
def mock_admin(app: FastAPI):
    user = User(
        **{
            "id": 1,
            "username": "admin",
            "roles": ["admin"],
            "iat": 1,
            "exp": 1,
            "type": "access",
        }
    )
    app.dependency_overrides = {
        admin_required: lambda: None,
        get_user: lambda: user,
        get_authenticated_user: lambda: user,
    }

    yield user


def _raise_http_exception_403():
    raise HTTPException(403)


def _raise_http_exception_401():
    raise HTTPException(401)


@pytest.fixture
def mock_user(app: FastAPI):
    user = User(
        **{
            "id": 2,
            "username": "user",
            "roles": [],
            "iat": 1,
            "exp": 1,
            "type": "access",
        }
    )

    app.dependency_overrides = {
        admin_required: _raise_http_exception_403,
        get_user: lambda: user,
        get_authenticated_user: lambda: user,
    }

    yield user


@pytest.fixture
def mock_unverified_user(app: FastAPI):
    user = User(
        **{
            "id": 4,
            "username": "unverified",
            "roles": [],
            "iat": 1,
            "exp": 1,
            "type": "access",
        }
    )
    app.dependency_overrides = {
        admin_required: _raise_http_exception_403,
        get_user: lambda: user,
        get_authenticated_user: lambda: user,
    }

    yield user


@pytest.fixture
def mock_banned_user(app: FastAPI):
    user = User(
        **{
            "id": 5,
            "username": "banned",
            "roles": [],
            "iat": 1,
            "exp": 1,
            "type": "access",
        }
    )
    app.dependency_overrides = {
        admin_required: _raise_http_exception_401,
        get_user: _raise_http_exception_401,
        get_authenticated_user: _raise_http_exception_401,
    }

    yield user


@pytest.fixture
def mock_social_user(app: FastAPI):
    user = User(
        **{
            "id": 3,
            "username": "social",
            "roles": [],
            "iat": 1,
            "exp": 1,
            "type": "access",
        }
    )
    app.dependency_overrides = {
        admin_required: _raise_http_exception_403,
        get_user: lambda: user,
        get_authenticated_user: lambda: user,
    }

    yield user


@pytest.fixture
def mock_social_user_with_password(app: FastAPI):
    user = User(
        **{
            "id": 6,
            "username": "social_with_password",
            "roles": [],
            "iat": 1,
            "exp": 1,
            "type": "access",
        }
    )
    app.dependency_overrides = {
        admin_required: _raise_http_exception_403,
        get_user: lambda: user,
        get_authenticated_user: lambda: user,
    }

    yield user


@pytest.fixture
def mock_anonim(app: FastAPI):
    user = Anonim()
    app.dependency_overrides[admin_required] = _raise_http_exception_403
    app.dependency_overrides[get_user] = lambda: user
    app.dependency_overrides[get_authenticated_user] = _raise_http_exception_401
    app.dependency_overrides = {
        admin_required: _raise_http_exception_403,
        get_user: lambda: user,
        get_authenticated_user: _raise_http_exception_401,
    }
    yield user
