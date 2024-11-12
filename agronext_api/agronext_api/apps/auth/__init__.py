from datetime import datetime, timedelta, timezone
from typing import Any, Dict
import msal
import jwt
from .auth_settings import auth_settings
from ...exceptions.auth import InvalidCredentialsError, AuthenticationError, InternalServerError



class AdAuthenticator:

    def __init__(self):
        self._client_id = auth_settings.CLIENT_ID
        self._client_secret = auth_settings.CLIENT_SECRET
        self._authority = auth_settings.AUTHORITY
        self._scope = ["https://graph.microsoft.com/.default"]
        self._secret_key = "dashjkdashukjasadas468d456asdasdijoasds88949ads645645asdasohjkdas"
        self._app = msal.ConfidentialClientApplication(
            client_id=self._client_id,
            client_credential=self._client_secret,
            authority=self._authority,
        )


    def authenticate(self, username: str, password: str):
        try:
            result = self._app.acquire_token_by_username_password(username=username, password=password, scopes=self._scope)
            if "access_token" in result:
                return self._generate_token(username=username, claims={})
            else:
                error_description = result.get("error_description", "Error Desconhecido na autenticação")
                if 'invalid_grant' in result.get('error', ''): 
                    raise InvalidCredentialsError(f"{error_description}") 
                else: 
                    raise AuthenticationError(f"{error_description}")
        except InvalidCredentialsError:
            raise
        except AuthenticationError:
            raise
        except Exception as e:
            raise InternalServerError(e)


    def _generate_token(self, username: str, claims: Dict[str, Any]) -> str:
        expiration = datetime.now(timezone.utc) + timedelta(hours=1)
        claims = { "sub": username, "exp": expiration, "custom_claims": claims } 
        token = jwt.encode(claims, self._secret_key, algorithm="HS256")
        return token
    
    def decode_token(self, token: str):
        return jwt.decode(token, self._secret_key, algorithms=["HS256"])