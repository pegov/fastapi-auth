from typing import Callable

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import ORJSONResponse

from fastapi_auth.backend.abc.authorization import AbstractAuthorization
from fastapi_auth.backend.abc.transport import AbstractTransport
from fastapi_auth.dependencies import get_authenticated_user
from fastapi_auth.errors import (
    AuthorizationError,
    TokenDecodingError,
    UserNotActiveError,
)
from fastapi_auth.jwt import JWT, TokenParams
from fastapi_auth.models.token import RefreshAccessTokenResponse, TokenPayloadResponse
from fastapi_auth.models.user import User
from fastapi_auth.repo import Repo


def get_token_router(
    get_repo: Callable,
    authorization: AbstractAuthorization,
    jwt: JWT,
    tp: TokenParams,
    transport: AbstractTransport,
) -> APIRouter:
    router = APIRouter()

    @router.post(
        "/token",
        name="token:payload",
        response_model=TokenPayloadResponse,
    )
    async def token_payload(user: User = Depends(get_authenticated_user)):
        return user

    @router.post(
        "/token/refresh",
        name="token:refresh_access_token",
        response_model=RefreshAccessTokenResponse,
    )
    async def token_refresh_access_token(
        request: Request,
        repo: Repo = Depends(get_repo),
    ):
        try:
            refresh_token = transport.get_refresh_token(request)
            payload = jwt.decode_token(refresh_token)
            user = User(**payload)
            await authorization.authorize(repo, user, "refresh")
            user_db = await repo.get(user.id)
            if not user_db.active:
                raise UserNotActiveError

            access_token = jwt.create_access_token(user_db.payload())
            response = ORJSONResponse({"access_token": access_token})
            transport.refresh_access_token(
                response, access_token, tp.access_token_expiration
            )
            return response

        except (TokenDecodingError, AuthorizationError):  # pragma: no cover
            raise HTTPException(401)

    return router
