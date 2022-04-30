import asyncio
from typing import Callable, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response

from fastapi_auth.dependencies import get_authenticated_user
from fastapi_auth.detail import Detail
from fastapi_auth.errors import (
    OAuthAccountAlreadyExistsError,
    OAuthAccountNotSetError,
    PasswordNotSetError,
    SameUsernameError,
    TokenAlreadyUsedError,
    UsernameAlreadyExistsError,
    WrongTokenTypeError,
)
from fastapi_auth.models.me import ChangeUsernameRequest, MeResponse
from fastapi_auth.models.user import User
from fastapi_auth.services.me import MeService


def get_me_router(
    service: MeService,
    on_update_action: Optional[Callable],
    debug: bool,
) -> APIRouter:
    router = APIRouter()

    @router.get(
        "/me",
        name="me:get",
        response_model=MeResponse,
        response_model_exclude_none=True,
    )
    async def me_get(
        *,
        user: User = Depends(get_authenticated_user),
    ):
        return await service.get(user)

    @router.post("/me/change_username", name="me:change_username")
    async def me_change_username(
        *,
        data_in: ChangeUsernameRequest,
        request: Request,
        user: User = Depends(get_authenticated_user),
    ):
        try:
            user, update_obj = await service.change_username(data_in, user)

            if on_update_action is not None:  # pragma: no cover
                if asyncio.iscoroutinefunction(on_update_action):
                    await on_update_action(request, user, update_obj)
                else:
                    on_update_action(request, user, update_obj)

        except SameUsernameError:  # pragma: no cover
            raise HTTPException(400, detail=Detail.SAME_USERNAME)
        except UsernameAlreadyExistsError:  # pragma: no cover
            raise HTTPException(400, detail=Detail.USERNAME_ALREADY_EXISTS)

    @router.post("/me/oauth/add_account/{provider_name}", name="me:add_oauth")
    async def me_add_oauth(
        provider_name: str,
        response: Response,
        user: User = Depends(get_authenticated_user),
    ):
        try:
            token = await service.add_oauth_account(provider_name, user)
        except OAuthAccountAlreadyExistsError:
            raise HTTPException(400, detail=Detail.OAUTH_ACCOUNT_ALREADY_EXISTS)
        response.set_cookie(
            key="add_oauth_account",
            value=token,
            max_age=60 * 3,
            secure=not debug,
            httponly=True,
        )

    @router.post(
        "/me/oauth/request_account_removal", name="me:request_oauth_account_removal"
    )
    async def me_request_account_removal(
        user: User = Depends(get_authenticated_user),
    ):
        try:
            await service.request_oauth_account_removal(user)
        except OAuthAccountNotSetError:
            raise HTTPException(400, detail=Detail.OAUTH_ACCOUNT_NOT_SET)
        except PasswordNotSetError:
            raise HTTPException(400, detail=Detail.PASSWORD_NOT_SET)

    @router.post("/me/oauth/remove_account/{token}", name="me:remove_oauth_account")
    async def me_remove_account(token: str):
        try:
            await service.remove_oauth_account(token)
        except WrongTokenTypeError:
            raise HTTPException(400, detail=Detail.WRONG_TOKEN_TYPE)
        except TokenAlreadyUsedError:
            raise HTTPException(400, detail=Detail.TOKEN_ALREADY_USED)

    return router
