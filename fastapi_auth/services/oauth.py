from fastapi_auth.repo import AuthRepo


async def resolve_username(repo: AuthRepo, email: str) -> str:
    username = email.split("@")[0]

    i = 0
    while True:
        postfix = str(i) if i > 0 else ""
        resolved_username = f"{username}{postfix}"
        existing_username = await repo.get_by_username(resolved_username)
        if existing_username is None:
            return resolved_username

        if i > 10_000:
            raise RuntimeError("something is wrong")