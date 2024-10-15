from pydantic import BaseModel as PydanticBaseModel, ConfigDict

class BaseModel(PydanticBaseModel):
    model_config = ConfigDict(
        extra='forbid', 
        frozen=True, 
        populate_by_name=True, 
        use_enum_values=True, 
        arbitrary_types_allowed=True, 
        from_attributes=True
    )