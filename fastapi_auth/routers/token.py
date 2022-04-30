from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import ORJSONResponse

from fastapi_auth.backend.abc.transport import AbstractTransport
from fastapi_auth.dependencies import get_authenticated_user
from fastapi_auth.errors import AuthorizationError, TokenDecodingError
from fastapi_auth.jwt import JWT
from fastapi_auth.models.token import RefreshAccessTokenResponse, TokenPayloadResponse
from fastapi_auth.models.user import User
from fastapi_auth.services.token import TokenService


def get_token_router(
    service: TokenService,
    jwt: JWT,
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
    async def token_refresh_access_token(request: Request):
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
