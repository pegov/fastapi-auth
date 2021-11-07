import asyncio
from typing import Callable

from fastapi import APIRouter, Depends, HTTPException, Request

from fastapi_auth.detail import HTTPExceptionDetail
from fastapi_auth.models.users import Me, UpdateMe
from fastapi_auth.repo import AuthRepo
from fastapi_auth.user import User


def get_users_router(
    repo: AuthRepo,
    get_authenticated_user: Callable,
    change_username_callback: Callable[[Request, int, str], None],
) -> APIRouter:
    router = APIRouter()

    @router.get(
        "/me",
        name="users:get_me",
        response_model=Me,
        response_model_exclude_none=True,
    )
    async def users_get_me(
        *,
        user: User = Depends(get_authenticated_user),
    ):
        return await repo.get(user.id)

    @router.patch("/me", name="users:update_me")
    async def users_update_me(
        *,
        data_in: UpdateMe,
        request: Request,
        user: User = Depends(get_authenticated_user),
    ):
        item = await repo.get(user.id)

        if data_in.username is not None:
            if data_in.username == item.get("username"):
                raise HTTPException(400, HTTPExceptionDetail.SAME_USERNAME)

            await repo.change_username(user.id, data_in.username)

            if change_username_callback is not None:
                if asyncio.iscoroutinefunction(change_username_callback):
                    await change_username_callback(request, user.id, data_in.username)  # type: ignore
                else:
                    change_username_callback(request, user.id, data_in.username)

            # TODO: replace access and refresh token

        if data_in.email is not None:
            if data_in.email == item.get("email"):
                raise HTTPException(400, HTTPExceptionDetail.SAME_EMAIL)
            await repo.change_email(user.id, data_in.email)

    return router