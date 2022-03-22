import pytest

from fastapi_auth.backend.abc.authorization import AbstractAuthorization
from fastapi_auth.backend.abc.captcha import AbstractCaptchaClient
from fastapi_auth.backend.abc.email import AbstractEmailClient
from fastapi_auth.backend.abc.password import AbstractPasswordBackend
from fastapi_auth.errors import (
    EmailAlreadyExistsError,
    InvalidCaptchaError,
    InvalidPasswordError,
    PasswordNotSetError,
    TimeoutError,
    UsernameAlreadyExistsError,
    UserNotActiveError,
    UserNotFoundError,
)
from fastapi_auth.jwt import JWT, TokenParams
from fastapi_auth.models.auth import LoginRequest, RegisterRequest
from fastapi_auth.models.user import UserDB
from fastapi_auth.repo import Repo
from fastapi_auth.services.auth import AuthService

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_service(
    mock_repo: Repo,
    mock_jwt: JWT,
    mock_authorization: AbstractAuthorization,
    mock_password_backend: AbstractPasswordBackend,
    mock_email_client: AbstractEmailClient,
    mock_captcha_client: AbstractCaptchaClient,
):
    yield AuthService(
        mock_repo,
        mock_jwt,
        TokenParams(),
        mock_authorization,
        mock_password_backend,
        mock_email_client,
        mock_captcha_client,
        False,
    )


async def test_register_error_invalid_captcha(mock_service: AuthService):
    data_in = RegisterRequest(
        email="newemail@gmail.com",
        username="newusername",
        password1="123456",
        password2="123456",
        captcha=None,
    )

    with pytest.raises(InvalidCaptchaError):
        await mock_service.register(data_in, "ip")


async def test_register_error_email_already_exists(mock_service: AuthService):
    data_in = RegisterRequest(
        email="example1@gmail.com",
        username="newusername",
        password1="123456",
        password2="123456",
        captcha="value",
    )

    with pytest.raises(EmailAlreadyExistsError):
        await mock_service.register(data_in, "ip")


async def test_register_error_username_already_exists(mock_service: AuthService):
    data_in = RegisterRequest(
        email="newemail@gmail.com",
        username="admin",
        password1="123456",
        password2="123456",
        captcha="value",
    )

    with pytest.raises(UsernameAlreadyExistsError):
        await mock_service.register(data_in, "ip")


async def test_register(mock_service: AuthService):
    data_in = RegisterRequest(
        email="newemail@gmail.com",
        username="newusername",
        password1="123456",
        password2="123456",
        captcha="value",
    )
    user = await mock_service.register(data_in, "ip")
    assert isinstance(user, UserDB)


async def test_login_error_timeout(mock_service: AuthService):
    data_in = LoginRequest(login="admin", password="123456")
    with pytest.raises(TimeoutError):
        for _ in range(100):
            await mock_service.login(data_in, "ip")


async def test_login_error_invalid_password(mock_service: AuthService):
    data_in = LoginRequest(login="admin", password="wrongpassword")
    with pytest.raises(InvalidPasswordError):
        await mock_service.login(data_in, "ip")


async def test_login_error_user_not_found(mock_service: AuthService):
    data_in = LoginRequest(login="notfound", password="wrongpassword")
    with pytest.raises(UserNotFoundError):
        await mock_service.login(data_in, "ip")


async def test_login_error_ban(mock_service: AuthService):
    data_in = LoginRequest(login="banned", password="123456")
    with pytest.raises(UserNotActiveError):
        await mock_service.login(data_in, "ip")


async def test_login_error_password_not_set(mock_service: AuthService):
    data_in = LoginRequest(login="social", password="wrongpassword")
    with pytest.raises(PasswordNotSetError):
        await mock_service.login(data_in, "ip")


async def test_login(mock_service: AuthService):
    data_in = LoginRequest(login="admin", password="123456")
    user = await mock_service.login(data_in, "ip")
    assert isinstance(user, UserDB)
