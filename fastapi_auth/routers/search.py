from typing import Optional

from fastapi import APIRouter, Depends

from fastapi_auth.core.user import admin_required
from fastapi_auth.services import SearchService


def get_router():

    router = APIRouter()

    @router.get("/{id}", name="search:user", dependencies=[Depends(admin_required)])
    async def get_user(id: int):
        service = SearchService()
        return await service.get_user(id)

    @router.get("", name="search:search", dependencies=[Depends(admin_required)])
    async def search(
        *, id: Optional[int] = None, username: Optional[str] = None, p: int = 1
    ):
        service = SearchService()
        return await service.search(id, username, p)

    return router
