from typing import Optional


class User:
    def __init__(self, data: Optional[dict] = None) -> None:
        self.data = data
        if data is not None:
            self.is_authenticated = True
            self.is_admin = "admin" in data.get("roles")
            self.id = int(data.get("id"))
            self.username = data.get("username")
            self.roles = data.get("roles")
        else:
            self.is_authenticated = False
            self.is_admin = False
            self.id = None
            self.username = None
            self.roles = []
