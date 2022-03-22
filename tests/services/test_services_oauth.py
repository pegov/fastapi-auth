from typing import Iterable

import pytest

from fastapi_auth.backend.abc.oauth import AbstractOAuthProvider
from fastapi_auth.errors import (
    EmailAlreadyExistsError,
    OAuthLoginOnlyError,
    UserNotActiveError,
)
from fastapi_auth.jwt import JWT, TokenParams
from fastapi_auth.models.user import UserDB
from fastapi_auth.repo import Repo
from fastapi_auth.services.oauth import OAuthService

pytestmark = pytest.mark.asyncio

ORIGIN = "origin"
REDIRECT = "/redirect"


@pytest.fixture
def mock_service(
    mock_repo: Repo,
    mock_jwt: JWT,
    mock_oauth_providers: Iterable[AbstractOAuthProvider],
):
    yield OAuthService(
        mock_repo,
        mock_jwt,
        TokenParams(),
        mock_oauth_providers,
        ORIGIN,
        REDIRECT,
    )


def test_get_provider_none(mock_service: OAuthService):
    assert mock_service.get_provider("wrong name") is None


def test_get_provider(
    mock_service: OAuthService,
    mock_oauth_providers: Iterable[AbstractOAuthProvider],
):
    name = mock_oauth_providers[0].name  # type: ignore
    assert mock_service.get_provider(name) is not None


def test_create_redirect_uri(
    mock_service: OAuthService,
):
    name = "name"
    assert (
        mock_service.create_redirect_uri(name) == f"{ORIGIN}{REDIRECT}/{name}/callback"
    )


async def test_get_user_error_ban(
    mock_service: OAuthService,
    mock_oauth_providers: Iterable[AbstractOAuthProvider],
):
    provider = mock_oauth_providers[0]  # type: ignore
    with pytest.raises(UserNotActiveError):
        await mock_service.get_user(provider, "5")


async def test_create_user_error_email_already_exists(
    mock_service: OAuthService,
    mock_oauth_providers: Iterable[AbstractOAuthProvider],
):
    provider = mock_oauth_providers[0]  # type: ignore
    with pytest.raises(EmailAlreadyExistsError):
        await mock_service.create_user(provider, "100", "example5@gmail.com")


async def test_create_user_error_login_only(
    mock_service: OAuthService,
    mock_oauth_providers: Iterable[AbstractOAuthProvider],
):
    provider = mock_oauth_providers[1]  # type: ignore
    with pytest.raises(OAuthLoginOnlyError):
        await mock_service.create_user(provider, "100", "example100@gmail.com")


async def get_user(
    mock_service: OAuthService,
    mock_oauth_providers: Iterable[AbstractOAuthProvider],
):
    provider = mock_oauth_providers[0]  # type: ignore
    user = await mock_service.get_user(provider, "3")
    assert isinstance(user, UserDB)


async def test_create_user(
    mock_service: OAuthService,
    mock_oauth_providers: Iterable[AbstractOAuthProvider],
):
    provider = mock_oauth_providers[0]  # type: ignore
    user = await mock_service.create_user(provider, "100", "example100@gmail.com")
    assert isinstance(user, UserDB)
