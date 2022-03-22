import asyncio
from typing import Callable, Optional

from fastapi import APIRouter, Depends, Request, Response
from fastapi.exceptions import HTTPException
from fastapi.responses import ORJSONResponse

from fastapi_auth.backend.abc.transport import AbstractTransport
from fastapi_auth.dependencies import get_authenticated_user
from fastapi_auth.detail import Detail
from fastapi_auth.errors import (
    AuthorizationError,
    EmailAlreadyExistsError,
    InvalidCaptchaError,
    InvalidPasswordError,
    TimeoutError,
    TokenDecodingError,
    UsernameAlreadyExistsError,
    UserNotActiveError,
    UserNotFoundError,
)
from fastapi_auth.jwt import JWT
from fastapi_auth.models.auth import (
    LoginRequest,
    RefreshAccessTokenResponse,
    RegisterRequest,
    UserPayloadResponse,
)
from fastapi_auth.models.user import User
from fastapi_auth.services.auth import AuthService


def get_auth_router(
    service: AuthService,
    jwt: JWT,
    transport: AbstractTransport,
    on_create_action: Optional[Callable],
) -> APIRouter:
    router = APIRouter()

    @router.post("/register", name="auth:register")
    async def auth_register(
        *,
        data_in: RegisterRequest,
        request: Request,
        response: Response,
    ):
        try:
            user_db = await service.register(data_in, request.client.host)

            if on_create_action is not None:  # pragma: no cover
                if asyncio.iscoroutinefunction(on_create_action):
                    await on_create_action(request, user_db)
                else:
                    on_create_action(request, user_db)

            access_token, refresh_token = jwt.create_tokens(user_db.payload())
            return transport.login(
                response,
                access_token,
                refresh_token,
                jwt.access_token_expiration,
                jwt.refresh_token_expiration,
            )

        except InvalidCaptchaError:  # pragma: no cover
            raise HTTPException(400, detail=Detail.INVALID_CAPTCHA)
        except UsernameAlreadyExistsError:  # pragma: no cover
            raise HTTPException(400, detail=Detail.EMAIL_ALREADY_EXISTS)
        except EmailAlreadyExistsError:  # pragma: no cover
            raise HTTPException(400, detail=Detail.USERNAME_ALREADY_EXISTS)

    @router.post("/login", name="auth:login")
    async def auth_login(
        request: Request,
        data_in: LoginRequest,
        response: Response,
    ):
        try:
            user_db = await service.login(
                data_in,
                request.client.host,
            )
            access_token, refresh_token = jwt.create_tokens(user_db.payload())
            return transport.login(
                response,
                access_token,
                refresh_token,
                jwt.access_token_expiration,
                jwt.refresh_token_expiration,
            )

        except UserNotActiveError:  # pragma: no cover
            raise HTTPException(400, detail=Detail.USER_NOT_ACTIVE)
        except InvalidPasswordError:  # pragma: no cover
            raise HTTPException(401)
        except UserNotFoundError:  # pragma: no cover
            raise HTTPException(404)
        except TimeoutError:  # pragma: no cover
            raise HTTPException(429)

    @router.post("/logout", name="auth:logout")
    async def auth_logout(response: Response):
        transport.logout(response)

    @router.post(
        "/token",
        name="auth:token",
        response_model=UserPayloadResponse,
    )
    async def auth_token(user: User = Depends(get_authenticated_user)):
        return user

    @router.post(
        "/token/refresh",
        name="auth:refresh_access_token",
        response_model=RefreshAccessTokenResponse,
    )
    async def auth_refresh_access_token(request: Request):
        try:
            refresh_token = transport.get_refresh_token(request)
            payload = jwt.decode_token(refresh_token)
            user = User(**payload)
            user_db = await service.authorize(user)
            access_token = jwt.create_access_token(user_db.payload())
            response = ORJSONResponse({"access_token": access_token})
            transport.refresh_access_token(
                response, access_token, jwt.access_token_expiration
            )
            return response

        except (TokenDecodingError, AuthorizationError):  # pragma: no cover
            raise HTTPException(401)

    return router
