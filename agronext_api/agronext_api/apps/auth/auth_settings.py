from typing import List
from ...config.base_settings import BaseSettings
from pydantic import Field


class AuthSettings(BaseSettings):
    CLIENT_ID: str = Field(default="", description="client id", env="AUTH_CLIENT_ID")
    CLIENT_SECRET: str = Field(default="", description="client secret", env="AUTH_CLIENT_SECRET")
    TENENT_ID: str = Field(default="", description="Tenent ID", env="AUTH_TENENT_ID")
    
    @property
    def GET_AUTHORITY(self) -> str:
        return f"https://login.microsoftonline.com/{self.TENENT_ID}"
    
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
    def USER_SCOPE(self) -> str:
        return {f"api://{self.CLIENT_ID}/user_impersonation" : "user_impersonation"}


auth_settings = AuthSettings()