from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MassLogoutStatusResponse(BaseModel):
    active: bool
    date: Optional[datetime] = None
