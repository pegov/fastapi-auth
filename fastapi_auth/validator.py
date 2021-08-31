from fastapi_auth.backend.validator import BaseUserValidator, StandardUserValidator


class Validator:
    _validator: BaseUserValidator = StandardUserValidator()

    # NOTE: setup again.
    @classmethod
    def set(cls, validator: BaseUserValidator) -> None:
        cls._validator = validator
