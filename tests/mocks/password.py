from fastapi_auth.backend.abc.password import AbstractPasswordBackend


class MockPasswordBackend(AbstractPasswordBackend):
    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return plain_password == hashed_password

    def hash(self, password: str) -> str:
        return password
