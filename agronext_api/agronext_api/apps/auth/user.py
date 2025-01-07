from typing import Optional

from pydantic import Field

from ...schemas import BaseModel


class User(BaseModel):
    id: Optional[str] = Field(default=None)
    email: Optional[str] = Field(default=None)
