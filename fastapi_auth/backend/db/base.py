from typing import Iterable, Optional, Tuple


class BaseDBBackend:
    async def get(self, id: int) -> Optional[dict]:
        raise NotImplementedError

    async def get_by_email(self, email: str) -> Optional[dict]:
        raise NotImplementedError

    async def get_by_username(self, username: str) -> Optional[dict]:
        raise NotImplementedError

    async def get_by_social(self, provider: str, sid: str) -> Optional[dict]:
        raise NotImplementedError

    async def create(self, obj: dict) -> int:
        """Create user, return id."""
        raise NotImplementedError

    async def update(self, id: int, obj: dict) -> bool:
        """Update user data, return True if success."""
        raise NotImplementedError

    async def delete(self, id: int) -> bool:
        """Delete user, return True if success."""
        raise NotImplementedError

    async def _count(self, query: Optional[dict]) -> int:
        raise NotImplementedError

    async def request_email_confirmation(self, email: str, token_hash: str) -> None:
        """Create email confirmation"""
        raise NotImplementedError

    async def confirm_email(self, token_hash: str) -> bool:
        """If success, return True."""
        raise NotImplementedError

    async def get_blacklist(self) -> Iterable[dict]:
        raise NotImplementedError

    async def search(
        self,
        id: Optional[int],
        username: Optional[str],
        p: int,
        size: int,
    ) -> Tuple[dict, int]:
        raise NotImplementedError
