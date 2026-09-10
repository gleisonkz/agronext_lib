from pydantic import BaseModel as PydanticBaseModel  # noqa: F401
from pydantic import (  # noqa: F401
    ConfigDict,
    EmailStr,
    Field,
    RootModel,
    computed_field,
)


class BaseModel(PydanticBaseModel):
    model_config = ConfigDict(
        extra="ignore",
        frozen=True,
        populate_by_name=True,
        use_enum_values=True,
        arbitrary_types_allowed=True,
        from_attributes=True,
    )
