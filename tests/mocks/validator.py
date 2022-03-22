from fastapi_auth.backend.abc.validator import AbstractValidator


class MockValidator(AbstractValidator):
    def validate_username(self, v: str) -> str:
        return v

    def validate_password(self, v: str, values) -> str:
        return v
