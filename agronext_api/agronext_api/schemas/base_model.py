from pydantic import BaseModel as PydanticBaseModel, ConfigDict


def to_camel(string: str) -> str:
    parts = string.split('_')
    return parts[0] + ''.join(word.capitalize() for word in parts[1:])



class BaseModel(PydanticBaseModel):
    model_config = ConfigDict(
        extra='forbid', 
        frozen=True, 
        populate_by_name=True, 
        use_enum_values=True, 
        arbitrary_types_allowed=True, 
        from_attributes=True,
        alias_generator=to_camel
    )

    