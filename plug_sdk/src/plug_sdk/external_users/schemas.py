from typing import Optional

from plug_sdk.base_model import BaseModel, EmailStr, Field, RootModel


class ExternalUserResponse(BaseModel):
    user_id: str


class CreateExternalUserRequest(BaseModel):
    email: EmailStr
    phone_number: str
    name: str


class CreateExternalUserResponse(ExternalUserResponse):
    pass


class UpdateExternalUserRequest(BaseModel):
    user_id: str
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    name: Optional[str] = None
    blocked: bool = False
    user_metadata: Optional[dict] = None


class UpdateExternalUserResponse(ExternalUserResponse):
    pass


class FilterExternalUsersRequest(BaseModel):
    id: Optional[str] = None
    email: Optional[EmailStr] = None
    username: Optional[str] = None


FilterExternalUsersResponse = RootModel[list[ExternalUserResponse]]
