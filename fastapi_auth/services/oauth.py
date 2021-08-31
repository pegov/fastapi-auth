from fastapi_auth.repo import AuthRepo
from fastapi_auth.utils.string import create_random_string

MAX_ATTEMPTS = 15


async def resolve_username(repo: AuthRepo, email: str) -> str:
    username = email.split("@")[0]

    i = 0
    while True:
        postfix = str(i) if i > 0 else ""
        resolved_username = f"{username}{postfix}"
        existing_username = await repo.get_by_username(resolved_username)
        if existing_username is None:
            return resolved_username

        i += 1

        if i > MAX_ATTEMPTS:
            postfix = create_random_string(6)
            resolved_username = f"{username}{postfix}"
            existing_username = await repo.get_by_username(resolved_username)
            if existing_username is None:
                return resolved_username

            raise RuntimeError("something is wrong")
