from fastapi_auth.backend.abc.validator import AbstractValidator
from fastapi_auth.backend.validator.default import DefaultUserValidator


class GlobalValidator:
    _validator: AbstractValidator = DefaultUserValidator()

    @classmethod
    def set(cls, validator: AbstractValidator) -> None:  # pragma: no cover
        cls._validator = validator
