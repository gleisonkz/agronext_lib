from typing import List
from ...config.base_settings import BaseSettings
from pydantic import Field


class AuthSettings(BaseSettings):
    CLIENT_ID: str = Field(default="", description="client id")
    CLIENT_SECRET: str = Field(default="", description="client secret")
    TENANT_ID: str = Field(default="", description="Tenant ID")
    GROUP_USERS_ID: str = Field(default="", description="Id do Grupo de usuários")
    CLIENT_OKTA_ID: str = Field(default="", description="Okta Client iD")

    @property
    def GET_AUTHORITY(self) -> str:
        return f"https://login.microsoftonline.com/{self.TENANT_ID}"

    @property
    def OPENAPI_AUTHORIZATION_URL(self) -> str:
        return f"https://login.microsoftonline.com/{self.TENANT_ID}/oauth2/v2.0/authorize"

    @property
    def OPENAPI_TOKEN_URL(self) -> str:
        return f"https://login.microsoftonline.com/{self.TENANT_ID}/oauth2/v2.0/token"

    @property
    def SCOPE_DEFAULT(self) -> List[str]:
        return ["https://graph.microsoft.com/.default"]

    @property
    def GRAPH_URL(self) -> str:
        return "https://graph.microsoft.com/v1.0/users"


    @property
    def GROUP_URL(self) -> str:
        return f"https://graph.microsoft.com/v1.0/groups/{self.GROUP_USERS_ID}/members"


    @property
    def USER_SCOPE(self) -> str:
        return {f"api://{self.CLIENT_ID}/user_impersonation": "user_impersonation"}

    @property
    def ISSUER_OKTA(self) -> str:
        return ""

    @property
    def AUDIENCE_OKTA(self) -> str:
        return ""


auth_settings = AuthSettings()
