from typing import Optional

from aioredis import Redis
from motor.motor_asyncio import AsyncIOMotorClient

from fastapi_auth.core.jwt import JWTBackend
from fastapi_auth.db.backend import MongoDBBackend, RedisBackend
from fastapi_auth.repositories import UsersRepo
from fastapi_auth.routers.admin import get_router as get_admin_router
from fastapi_auth.routers.auth import get_router as get_auth_router
from fastapi_auth.routers.password import get_router as get_password_router
from fastapi_auth.routers.search import get_router as get_search_router
from fastapi_auth.routers.social import get_router as get_social_router
from fastapi_auth.services import AuthService
from fastapi_auth.services.admin import AdminService
from fastapi_auth.services.password import PasswordService
from fastapi_auth.services.search import SearchService
from fastapi_auth.services.social import SocialService


class FastAPIAuth:
    def __init__(
        self,
        debug=False,
        language="RU",
        base_url="http://127.0.0.1",
        site: str = "127.0.0.1",
        database_name: str = "users",
        jwt_algorithm: str = "RS256",
        access_expiration: int = 60 * 60 * 6,
        refresh_expiration: int = 60 * 60 * 24 * 30,
        private_key: bytes = b"",
        public_key: bytes = b"",
        smtp_username: str = "",
        smtp_password: str = "",
        smtp_host: str = "",
        smtp_tls: int = 587,
        smtp_ssl: int = 465,
        recaptcha_secret: str = "",
        social_providers=(
            "vk",
            "google",
            "facebook",
        ),
        social_options: Optional[dict] = None
        # facebook_client_id: str = None,
        # facebook_client_secret: str = None,
        # vk_app_id: str = None,
        # vk_app_secret: str = None,
        # google_client_id: str = None,
        # google_client_secret: str = None,
    ):

        JWTBackend.create(
            jwt_algorithm,
            private_key,
            public_key,
            access_expiration,
            refresh_expiration,
        )

        self._database_backend = MongoDBBackend(database_name)
        self._cache_backend = RedisBackend()

        users_repo = UsersRepo(
            self._database_backend, self._cache_backend, access_expiration
        )

        self._debug = debug
        self._access_expiration = access_expiration
        self._refresh_expiration = refresh_expiration
        self._social_providers = social_providers

        AuthService.set_repo(users_repo)
        AuthService.init(
            debug,
            recaptcha_secret,
            smtp_username,
            smtp_password,
            smtp_host,
            smtp_tls,
            language,
            base_url,
            site,
        )
        SocialService.set_repo(users_repo)
        SocialService.init(language, base_url, social_options)
        AdminService.set_repo(users_repo)
        SearchService.set_repo(users_repo)
        PasswordService.set_repo(users_repo)

    def set_cache(self, cache: Redis) -> None:
        JWTBackend.set_cache(cache)
        self._cache_backend.set_cache(cache)

    def set_database(self, database: AsyncIOMotorClient) -> None:
        self._database_backend.set_client(database)

    @property
    def auth_router(self):
        return get_auth_router(
            self._debug, self._access_expiration, self._refresh_expiration
        )

    @property
    def social_router(self):
        return get_social_router(
            self._debug,
            self._access_expiration,
            self._refresh_expiration,
            self._social_providers,
        )

    @property
    def password_router(self):
        return get_password_router()

    @property
    def admin_router(self):
        return get_admin_router()

    @property
    def search_router(self):
        return get_search_router()
