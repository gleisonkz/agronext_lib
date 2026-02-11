from typing import Optional, Any

from plug_sdk.base_model import BaseModel, EmailStr, Field, RootModel


class BaseUserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    type_id: int
    external_id: Optional[str] = Field(
        default=None, description="ID of the user in the external system."
    )
    user_metadata: dict[str, Any]


class ExternalUserResponse(BaseUserResponse):
    email_verified: bool = Field(default=False)
    name: str
    phone_number: str
    blocked: bool = Field(default=False)
    user_metadata: Optional[dict] = Field(
        default=None, description="Metadata associated with the user."
    )


class CreateExternalUserRequest(BaseModel):
    email: EmailStr
    phone_number: str
    name: str


class CreateExternalUserResponse(BaseModel):
    message: str
    user_data: BaseUserResponse


class UpdateExternalUserRequest(BaseModel):
    user_id: str
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    name: Optional[str] = None
    blocked: bool = False
    user_metadata: Optional[dict] = None


class UpdateExternalUserResponse(BaseModel):
    message: str


class FilterExternalUsersRequest(BaseModel):
    id: Optional[str] = None
    email: Optional[EmailStr] = None
    username: Optional[str] = None


class FilterExternalUsersResponse(BaseModel):
    data: list[ExternalUserResponse] = Field(
        default_factory=list,
        description="List of external users matching the filter criteria.",
    )
