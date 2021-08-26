class BaseUserValidator:
    def validate_username(self, v: str) -> str:
        raise NotImplementedError

    def validate_password(self, v: str, values) -> str:
        raise NotImplementedError
