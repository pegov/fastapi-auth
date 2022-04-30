from fastapi_auth.backend.abc.jwt import AbstractJWTBackend
from fastapi_auth.jwt import TokenParams


class MockJWTBackend(AbstractJWTBackend):
    def create_token(self, type: str, payload: dict, expiration: int) -> str:
        return f"{type} token"

    def decode_token(self, token: str) -> dict:
        if token == "verify_wrong_type":
            return {
                "id": 1,
                "email": "whatever",
                "type": "wrong",
            }
        elif token == "verify_email_already_verified":
            return {
                "id": 1,
                "email": "example1@gmail.com",
                "type": TokenParams.verify_email_token_type,
            }
        elif token == "verify_email_mismatch":
            return {
                "id": 4,
                "email": "wrongemail@gmail.com",
                "type": TokenParams.verify_email_token_type,
            }
        elif token == "verify":
            return {
                "id": 4,
                "email": "example4@gmail.com",
                "type": TokenParams.verify_email_token_type,
            }
        elif token == "token_2_refresh":
            return {
                "id": 2,
                "username": "user",
                "roles": [],
                "iat": 1,
                "exp": 1,
                "type": "refresh",
            }
        elif token == "reset_password":
            return {
                "id": 2,
                "type": TokenParams.reset_password_token_type,
            }
        elif token == "reset_password_wrong_token_type":
            return {
                "id": 2,
                "type": TokenParams.reset_password_token_type + "wrong",
            }
        elif token == "verify_old_email":
            return {
                "id": 2,
                "email": "newemail@gmail.com",
                "type": TokenParams.check_old_email_token_type,
            }
        elif token == "verify_new_email":
            return {
                "id": 2,
                "email": "newemail@gmail.com",
                "type": TokenParams.check_new_email_token_type,
            }

        return {}
