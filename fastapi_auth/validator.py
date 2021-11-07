from fastapi_auth.backend.abc import AbstractUserValidator
from fastapi_auth.backend.validator import StandardUserValidator


class Validator:
    _validator: AbstractUserValidator = StandardUserValidator()

    # NOTE: setup again.
    @classmethod
    def set(cls, validator: AbstractUserValidator) -> None:
        cls._validator = validator  # pragma: no cover
