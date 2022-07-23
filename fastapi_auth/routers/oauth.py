import asyncio
import hashlib
import os
from typing import Callable, Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from fastapi_auth.backend.abc.transport import AbstractTransport
from fastapi_auth.errors import (
    EmailAlreadyExistsError,
    OAuthLoginOnlyError,
    TokenDecodingError,
    UserNotActiveError,
    WrongTokenTypeError,
)
from fastapi_auth.jwt import JWT, TokenParams
from fastapi_auth.oauth_messages import OAuthMessages
from fastapi_auth.repo import Repo
from fastapi_auth.services.oauth import OAuthService


def get_oauth_router(
    get_repo: Callable,
    service: OAuthService,
    jwt: JWT,
    tp: TokenParams,
    transport: AbstractTransport,
    message_path: str,
    on_create_action: Optional[Callable],
):
    router = APIRouter()

    @router.get("/{provider_name}", name="oauth:login")
    async def oauth_login(provider_name: str, request: Request):
        provider = service.get_provider(provider_name)
        if provider is None:  # pragma: no cover
            return RedirectResponse(
                f"{message_path}?message={OAuthMessages.PROVIDER_NOT_FOUND}"
            )

        state = hashlib.sha256(os.urandom(1024)).hexdigest()
        request.session["state"] = state

        redirect_uri = service.create_redirect_uri(provider_name)
        oauth_uri = provider.create_oauth_uri(redirect_uri, state)

        return RedirectResponse(oauth_uri)

    @router.get("/{provider_name}/callback", name="oauth:callback")
    async def oauth_callback(
        provider_name: str,
        request: Request,
        repo: Repo = Depends(get_repo),
    ):
        provider = service.get_provider(provider_name)
        if provider is None:
            return RedirectResponse(
                f"{message_path}?message={OAuthMessages.PROVIDER_NOT_FOUND}"
            )

        request_state = request.query_params.get("state")
        session_state = request.session.get("state")

        if request_state != session_state:
            return RedirectResponse(
                f"{message_path}?message={OAuthMessages.INVALID_STATE}"
            )

        redirect_uri = service.create_redirect_uri(provider_name)
        code = request.query_params.get("code")
        sid, email = await provider.get_user_data(redirect_uri, code)

        add_token = request.cookies.get("add_oauth_account")
        if add_token is not None:
            try:
                await service.add_oauth_account(repo, add_token, provider_name, sid)
                response = RedirectResponse(
                    f"/{message_path}?message={OAuthMessages.OAUTH_ACCOUNT_WAS_ADDED_SUCCESSFULLY}"
                )
            except WrongTokenTypeError:
                response = RedirectResponse(
                    f"/{message_path}?message={OAuthMessages.WRONG_TOKEN_TYPE}"
                )
            except TokenDecodingError:
                response = RedirectResponse(
                    f"/{message_path}?message={OAuthMessages.WRONG_TOKEN}"
                )

            response.delete_cookie("add_oauth_account")
            return response

        if email is None:
            return RedirectResponse(f"{message_path}?message={OAuthMessages.NO_EMAIL}")

        try:
            user_db = await service.get_user(repo, provider, sid)
            if user_db is None:
                user_db = await service.create_user(repo, provider, sid, email)

                if on_create_action is not None:  # pragma: no cover
                    if asyncio.iscoroutinefunction(on_create_action):
                        await on_create_action(request, user_db)
                    else:
                        on_create_action(request, user_db)

            access_token, refresh_token = jwt.create_tokens(user_db.payload())
            response = RedirectResponse("/")
            transport.login(
                response,
                access_token,
                refresh_token,
                tp.access_token_expiration,
                tp.refresh_token_expiration,
            )

        except UserNotActiveError:
            return RedirectResponse(f"{message_path}?message={OAuthMessages.BAN}")
        except EmailAlreadyExistsError:
            return RedirectResponse(
                f"{message_path}?message={OAuthMessages.EMAIL_ALREADY_EXISTS}"
            )
        except OAuthLoginOnlyError:
            return RedirectResponse(
                f"{message_path}?message={OAuthMessages.LOGIN_ONLY}"
            )

        return response

    return router
