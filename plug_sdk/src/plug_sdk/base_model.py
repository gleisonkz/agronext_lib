from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, Field, computed_field, model_validator  # noqa: F401


class BaseModel(PydanticBaseModel):
    model_config = ConfigDict(
        extra="ignore",
        frozen=True,
        populate_by_name=True,
        use_enum_values=True,
        arbitrary_types_allowed=True,
        from_attributes=True,
    )
