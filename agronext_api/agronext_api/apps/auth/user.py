from pydantic import Field

from ...schemas import BaseModel
from typing import Optional


class User(BaseModel):
    id: Optional[str] = Field(default=None)
    email: Optional[str] = Field(default=None)
