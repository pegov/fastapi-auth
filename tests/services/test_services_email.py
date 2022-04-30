import pytest

from fastapi_auth.backend.abc.email import AbstractEmailClient
from fastapi_auth.errors import (
    EmailAlreadyVerifiedError,
    EmailMismatchError,
    SameEmailError,
    TimeoutError,
    WrongTokenTypeError,
)
from fastapi_auth.jwt import JWT, TokenParams
from fastapi_auth.models.email import ChangeEmailRequest
from fastapi_auth.models.user import User
from fastapi_auth.repo import Repo
from fastapi_auth.services.email import EmailService

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_service(
    mock_repo: Repo,
    mock_jwt: JWT,
    mock_email_client: AbstractEmailClient,
):
    yield EmailService(
        mock_repo,
        mock_jwt,
        TokenParams(),
        mock_email_client,
    )


async def test_request_error_email_already_verified(
    mock_service: EmailService,
    mock_user: User,
):
    with pytest.raises(EmailAlreadyVerifiedError):
        await mock_service.request_verification(mock_user)


async def test_request(
    mock_service: EmailService,
    mock_unverified_user: User,
):
    await mock_service.request_verification(mock_unverified_user)


async def test_request_error_timeout(
    mock_service: EmailService,
    mock_unverified_user: User,
):
    with pytest.raises(TimeoutError):
        await mock_service.request_verification(mock_unverified_user)
        await mock_service.request_verification(mock_unverified_user)
        await mock_service.request_verification(mock_unverified_user)
        await mock_service.request_verification(mock_unverified_user)


async def test_verify_error_wrong_token_type(
    mock_service: EmailService,
):
    with pytest.raises(WrongTokenTypeError):
        await mock_service.verify("verify_wrong_type")


async def test_verify_error_email_already_verified(
    mock_service: EmailService,
):
    with pytest.raises(EmailAlreadyVerifiedError):
        await mock_service.verify("verify_email_already_verified")


async def test_verify_error_email_mismatch(
    mock_service: EmailService,
):
    with pytest.raises(EmailMismatchError):
        await mock_service.verify("verify_email_mismatch")


async def test_verify(
    mock_service: EmailService,
):
    await mock_service.verify("verify")


async def test_request_email_change_error_same_email(
    mock_service: EmailService, mock_user: User
):
    data_in = ChangeEmailRequest(email="example2@gmail.com")
    with pytest.raises(SameEmailError):
        await mock_service.request_email_change(data_in, mock_user)


async def test_request_email_change_error_timeout(
    mock_service: EmailService, mock_user: User
):
    data_in = ChangeEmailRequest(email="newemail@gmail.com")
    with pytest.raises(TimeoutError):
        for _ in range(10):
            await mock_service.request_email_change(data_in, mock_user)
