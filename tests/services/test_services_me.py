import pytest

from fastapi_auth.backend.abc.email import AbstractEmailClient
from fastapi_auth.errors import (
    SameEmailError,
    SameUsernameError,
    UsernameAlreadyExistsError,
)
from fastapi_auth.jwt import JWT, TokenParams
from fastapi_auth.models.me import ChangeEmailRequest, ChangeUsernameRequest
from fastapi_auth.models.user import User
from fastapi_auth.repo import Repo
from fastapi_auth.services.me import MeService

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_service(
    mock_repo: Repo,
    mock_jwt: JWT,
    mock_email_client: AbstractEmailClient,
):
    yield MeService(mock_repo, mock_jwt, TokenParams(), mock_email_client)


async def test_get(mock_service: MeService, mock_user: User):
    user = await mock_service.get(mock_user)
    assert user is not None


async def test_change_username_error_same_username(
    mock_service: MeService, mock_user: User
):
    data_in = ChangeUsernameRequest(username="user")
    with pytest.raises(SameUsernameError):
        await mock_service.change_username(data_in, mock_user)


async def test_change_username_error_username_already_exists(
    mock_service: MeService, mock_user: User
):
    data_in = ChangeUsernameRequest(username="admin")
    with pytest.raises(UsernameAlreadyExistsError):
        await mock_service.change_username(data_in, mock_user)


async def test_change_username(mock_service: MeService, mock_user: User):
    data_in = ChangeUsernameRequest(username="newuser")
    await mock_service.change_username(data_in, mock_user)


async def test_request_email_change_error_same_email(
    mock_service: MeService, mock_user: User
):
    data_in = ChangeEmailRequest(email="example2@gmail.com")
    with pytest.raises(SameEmailError):
        await mock_service.request_email_change(data_in, mock_user)


async def test_request_email_change_error_timeout(
    mock_service: MeService, mock_user: User
):
    data_in = ChangeEmailRequest(email="newemail@gmail.com")
    with pytest.raises(TimeoutError):
        for _ in range(10):
            await mock_service.request_email_change(data_in, mock_user)


async def test_request_oauth_account_removal(
    mock_service: MeService, mock_social_user_with_password: User
):
    await mock_service.request_oauth_account_removal(mock_social_user_with_password)
