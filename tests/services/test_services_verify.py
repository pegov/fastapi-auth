import pytest

from fastapi_auth.backend.abc.email import AbstractEmailClient
from fastapi_auth.errors import (
    EmailAlreadyVerifiedError,
    EmailMismatchError,
    TimeoutError,
    WrongTokenTypeError,
)
from fastapi_auth.jwt import JWT, TokenParams
from fastapi_auth.models.user import User
from fastapi_auth.repo import Repo
from fastapi_auth.services.verify import VerifyService

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_service(
    mock_repo: Repo,
    mock_jwt: JWT,
    mock_email_client: AbstractEmailClient,
):
    yield VerifyService(
        mock_repo,
        mock_jwt,
        TokenParams(),
        mock_email_client,
    )


async def test_get_status_unverified(
    mock_service: VerifyService, mock_unverified_user: User
):
    status = await mock_service.get_status(mock_unverified_user)
    assert status.verified is False


async def test_get_status_verified(mock_service: VerifyService, mock_user: User):
    status = await mock_service.get_status(mock_user)
    assert status.verified is True


async def test_request_error_email_already_verified(
    mock_service: VerifyService,
    mock_user: User,
):
    with pytest.raises(EmailAlreadyVerifiedError):
        await mock_service.request(mock_user)


async def test_request(
    mock_service: VerifyService,
    mock_unverified_user: User,
):
    await mock_service.request(mock_unverified_user)


async def test_request_error_timeout(
    mock_service: VerifyService,
    mock_unverified_user: User,
):
    with pytest.raises(TimeoutError):
        await mock_service.request(mock_unverified_user)
        await mock_service.request(mock_unverified_user)
        await mock_service.request(mock_unverified_user)
        await mock_service.request(mock_unverified_user)


async def test_verify_error_wrong_token_type(
    mock_service: VerifyService,
):
    with pytest.raises(WrongTokenTypeError):
        await mock_service.verify("verify_wrong_type")


async def test_verify_error_email_already_verified(
    mock_service: VerifyService,
):
    with pytest.raises(EmailAlreadyVerifiedError):
        await mock_service.verify("verify_email_already_verified")


async def test_verify_error_email_mismatch(
    mock_service: VerifyService,
):
    with pytest.raises(EmailMismatchError):
        await mock_service.verify("verify_email_mismatch")


async def test_verify(
    mock_service: VerifyService,
):
    await mock_service.verify("verify")
