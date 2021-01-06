from fastapi_auth.repositories import UsersRepo


class BaseService:
    _repo: UsersRepo

    @classmethod
    def set_repo(cls, repo: UsersRepo) -> None:
        cls._repo = repo
