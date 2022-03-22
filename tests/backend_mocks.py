import pytest

from fastapi_auth.backend.abc.cache import AbstractCacheClient
from fastapi_auth.backend.abc.db import AbstractDatabaseClient
from fastapi_auth.backend.abc.jwt import AbstractJWTBackend
from fastapi_auth.jwt import JWT
from fastapi_auth.repo import Repo
from tests.mocks import (
    MockAuthorization,
    MockCacheClient,
    MockCaptchaClient,
    MockDatabaseClient,
    MockEmailClient,
    MockJWTBackend,
    MockLoginOnlyOAuthProvider,
    MockOAuthProvider,
    MockPasswordBackend,
    MockTransport,
    MockValidator,
)


@pytest.fixture
def mock_jwt_backend():
    yield MockJWTBackend()


@pytest.fixture
def mock_jwt(mock_jwt_backend: AbstractJWTBackend):
    yield JWT(mock_jwt_backend, 60, 60)


@pytest.fixture
def mock_authorization():
    yield MockAuthorization()


@pytest.fixture
def mock_cache():
    yield MockCacheClient()


@pytest.fixture
def mock_captcha_client():
    yield MockCaptchaClient()


@pytest.fixture
def mock_db():
    yield MockDatabaseClient()


@pytest.fixture
def mock_repo(
    mock_db: AbstractDatabaseClient,
    mock_cache: AbstractCacheClient,
):
    yield Repo(mock_db, mock_cache, 60, 60)


@pytest.fixture
def mock_oauth_providers():
    yield (
        MockOAuthProvider(),
        MockLoginOnlyOAuthProvider(),
    )


@pytest.fixture
def mock_password_backend():
    yield MockPasswordBackend()


@pytest.fixture
def mock_email_client():
    yield MockEmailClient()


@pytest.fixture
def mock_validator():
    yield MockValidator()


@pytest.fixture
def mock_transport():
    yield MockTransport(
        "a",
        "r",
        False,
    )
