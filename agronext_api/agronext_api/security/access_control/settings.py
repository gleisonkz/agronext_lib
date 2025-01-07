from ...config.base_settings import BaseSettings


class AccessControlSettings(BaseSettings):
    client_id: str = "your_client_id"
    client_secret: str = "your_client_secret"
    issuer: str = "oidc_issuer"
    redirect_uri: str = "oidc_redirect_uri"
    scope: str = "openid email profile"
