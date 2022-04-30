import asyncio
from typing import Callable, Optional

from fastapi import APIRouter, Request, Response
from fastapi.exceptions import HTTPException

from fastapi_auth.backend.abc.transport import AbstractTransport
from fastapi_auth.detail import Detail
from fastapi_auth.errors import (
    EmailAlreadyExistsError,
    InvalidCaptchaError,
    InvalidPasswordError,
    TimeoutError,
    UsernameAlreadyExistsError,
    UserNotActiveError,
    UserNotFoundError,
)
from fastapi_auth.jwt import JWT
from fastapi_auth.models.auth import LoginRequest, RegisterRequest
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

    return router
