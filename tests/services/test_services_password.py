import pytest

from fastapi_auth.backend.abc.captcha import AbstractCaptchaClient
from fastapi_auth.backend.abc.email import AbstractEmailClient
from fastapi_auth.backend.abc.password import AbstractPasswordBackend
from fastapi_auth.errors import (
    InvalidCaptchaError,
    InvalidPasswordError,
    PasswordAlreadyExistsError,
    PasswordNotSetError,
    TimeoutError,
    UserNotFoundError,
    WrongTokenTypeError,
)
from fastapi_auth.jwt import JWT, TokenParams
from fastapi_auth.models.password import (
    PasswordChangeRequest,
    PasswordForgotRequest,
    PasswordResetRequest,
    PasswordSetRequest,
    PasswordStatusResponse,
)
from fastapi_auth.models.user import User
from fastapi_auth.repo import Repo
from fastapi_auth.services.password import PasswordService

pytestmark = pytest.mark.asyncio

PASSWORD = "123456"


@pytest.fixture
def mock_service(
    mock_repo: Repo,
    mock_jwt: JWT,
    mock_password_backend: AbstractPasswordBackend,
    mock_email_client: AbstractEmailClient,
    mock_captcha_client: AbstractCaptchaClient,
):
    yield PasswordService(
        mock_repo,
        mock_jwt,
        TokenParams(),
        mock_password_backend,
        mock_email_client,
        mock_captcha_client,
        False,
    )


async def test_get_status(mock_service: PasswordService, mock_user: User):
    m = await mock_service.get_status(mock_user)
    assert isinstance(m, PasswordStatusResponse)
    assert m.has_password


async def test_set_error_password_already_exists(
    mock_service: PasswordService, mock_user: User
):
    data_in = PasswordSetRequest(password1=PASSWORD, password2=PASSWORD)
    with pytest.raises(PasswordAlreadyExistsError):
        await mock_service.set(data_in, mock_user)


async def test_set(mock_service: PasswordService, mock_social_user: User):
    data_in = PasswordSetRequest(password1=PASSWORD, password2=PASSWORD)
    await mock_service.set(data_in, mock_social_user)


async def test_change_error_no_password(
    mock_service: PasswordService,
    mock_social_user: User,
):
    password = "123456"
    data_in = PasswordChangeRequest(
        old_password="123456", password1=password, password2=password
    )
    with pytest.raises(PasswordNotSetError):
        await mock_service.change(data_in, mock_social_user)


async def test_change_error_wrong_old_password(
    mock_service: PasswordService,
    mock_user: User,
):
    password = "wrongpassword"
    data_in = PasswordChangeRequest(
        old_password="wrongpassword",
        password1=password,
        password2=password,
    )
    with pytest.raises(InvalidPasswordError):
        await mock_service.change(data_in, mock_user)


async def test_change(mock_service: PasswordService, mock_user: User):
    data_in = PasswordChangeRequest(
        old_password=PASSWORD,
        password1=PASSWORD,
        password2=PASSWORD,
    )
    await mock_service.change(data_in, mock_user)


async def test_forgot_error_invalid_captcha(mock_service: PasswordService):
    data_in = PasswordForgotRequest(email="example1@gmail.com", captcha=None)
    with pytest.raises(InvalidCaptchaError):
        await mock_service.forgot(data_in)


async def test_forgot_error_user_not_found(mock_service: PasswordService):
    data_in = PasswordForgotRequest(email="notfound@gmail.com", captcha="value")
    with pytest.raises(UserNotFoundError):
        await mock_service.forgot(data_in)


async def test_forgot_error_timeout(mock_service: PasswordService):
    data_in = PasswordForgotRequest(email="example1@gmail.com", captcha="value")
    with pytest.raises(TimeoutError):
        await mock_service.forgot(data_in)
        await mock_service.forgot(data_in)
        await mock_service.forgot(data_in)
        await mock_service.forgot(data_in)


async def test_forgot(mock_service: PasswordService):
    data_in = PasswordForgotRequest(email="example1@gmail.com", captcha="value")
    await mock_service.forgot(data_in)


async def test_reset_error_wrong_token_type(mock_service: PasswordService):
    data_in = PasswordResetRequest(
        token="reset_password_wrong_token_type",
        password1=PASSWORD,
        password2=PASSWORD,
    )
    with pytest.raises(WrongTokenTypeError):
        await mock_service.reset(data_in)
