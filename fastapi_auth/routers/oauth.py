import asyncio
from typing import Callable, Iterable, Optional, Type

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from fastapi_auth.backend.auth import BaseJWTAuthentication
from fastapi_auth.backend.oauth import BaseOAuthProvider
from fastapi_auth.models.auth import BaseUserTokenPayload
from fastapi_auth.models.oauth import OAuthCreate
from fastapi_auth.repo import AuthRepo
from fastapi_auth.services.oauth import resolve_username
from fastapi_auth.utils.string import create_random_state


def get_router(
    repo: AuthRepo,
    auth_backend: BaseJWTAuthentication,
    oauth_providers: Iterable[BaseOAuthProvider],
    user_token_payload_model: Type[BaseUserTokenPayload],
    user_create_hook: Optional[Callable[[dict], None]],
    origin: str,
    create_redirect_path_prefix: str,
    error_redirect_path: str,
):
    def create_redirect_uri(provider_name: str) -> str:
        return f"{origin}{create_redirect_path_prefix}/{provider_name}/callback"

    def get_provider(provider_name: str) -> BaseOAuthProvider:
        for provider in oauth_providers:
            if provider.name == provider_name:
                return provider

        raise HTTPException(404)

    router = APIRouter()

    @router.get("/{provider_name}", name="oauth:login")
    async def oauth_login(provider_name: str, request: Request):
        provider = get_provider(provider_name)

        state = create_random_state()
        request.session["state"] = state

        redirect_uri = create_redirect_uri(provider_name)
        oauth_uri = provider.create_oauth_uri(redirect_uri, state)

        return RedirectResponse(oauth_uri)

    @router.get("/{provider_name}/callback", name="oauth:callback")
    async def oauth_callback(provider_name: str, request: Request):
        provider = get_provider(provider_name)

        request_state = request.query_params.get("state")
        session_state = request.session.get("state")

        if request_state != session_state:
            return RedirectResponse(f"{error_redirect_path}?message=invalid_state")

        redirect_uri = create_redirect_uri(provider_name)
        code = request.query_params.get("code")
        sid, email = await provider.get_user_data(redirect_uri, code)

        if email is None:
            return RedirectResponse(f"{error_redirect_path}?message=no_email")

        existing_social_user = await repo.get_by_social(provider_name, sid)
        if existing_social_user is not None:
            item = existing_social_user
            if not item.get("active"):
                return RedirectResponse(f"{error_redirect_path}?message=ban")
        else:
            existing_email = await repo.get_by_email(email)
            if existing_email is not None:
                return RedirectResponse(
                    f"{error_redirect_path}?message=email_already_exists"
                )

            username = await resolve_username(repo, email)

            user = OAuthCreate(
                **{
                    "email": email,
                    "username": username,
                    "provider": provider_name,
                    "sid": sid,
                }
            ).dict()
            id = await repo.create(user)
            user.update({"id": id})
            if user_create_hook is not None:
                if asyncio.iscoroutinefunction(user_create_hook):
                    await user_create_hook(user)  # type: ignore
                else:
                    user_create_hook(user)
            item = user

        payload = user_token_payload_model(**item).dict()
        access_token, refresh_token = auth_backend.create_tokens(payload)
        response = RedirectResponse("/")
        auth_backend.set_login_response(response, access_token, refresh_token)
        return response

    return router
