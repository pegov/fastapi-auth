from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class MassLogoutStatusResponse(BaseModel):
    active: bool
    date: Optional[datetime] = None


class SetRolesRequest(BaseModel):
    roles: List[str]
