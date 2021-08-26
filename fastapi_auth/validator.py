from fastapi_auth.backend.validator import BaseUserValidator


class Validator:
    _validator: BaseUserValidator

    # NOTE: setup again.
    @classmethod
    def setup(cls, validator: BaseUserValidator) -> None:
        cls._validator = validator
