from fastapi import Request

from fastapi_auth.backend.transport.cookie import CookieTransport


class MockTransport(CookieTransport):
    def get_refresh_token(self, request: Request) -> str:
        return "token_2_refresh"
