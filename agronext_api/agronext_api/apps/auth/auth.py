import functools

import msal
from fastapi_azure_auth import SingleTenantAzureAuthorizationCodeBearer
from fastapi_azure_auth.user import User as UserAuth
from .user import User
from fastapi import Request, Depends
from fastapi.security import SecurityScopes
from .auth_settings import auth_settings
from ...exceptions.auth import AuthenticationError, UnauthorizedError
from .profiles import resource_permissions, SystemFeature, Role
from okta_jwt_verifier import BaseJWTVerifier
from typing import Dict, List, Optional
import httpx

app_msal = msal.ConfidentialClientApplication(
    client_id=auth_settings.CLIENT_ID,
    authority=auth_settings.GET_AUTHORITY,
    client_credential=auth_settings.CLIENT_SECRET
)

auth_scheme = SingleTenantAzureAuthorizationCodeBearer(
    app_client_id=auth_settings.CLIENT_ID,
    tenant_id=auth_settings.TENENT_ID,
    scopes=auth_settings.USER_SCOPE,

)


#jwt_verifier = BaseJWTVerifier(
#    issuer=auth_settings.ISSUER_OKTA,
#    audience=auth_settings.AUDIENCE_OKTA,
#    client_id=auth_settings.CLIENT_OKTA_ID
#)


def verify_additional_rules(user_roles, method, additional_roles: List[Dict[str, list]]) -> bool:
    for additional_role in additional_roles:
        methods = additional_role.get("methods", [])
        return any(role in user_roles for role in additional_role.get("roles", [])) and method in methods


def verify_roles(roles: List[Role], user_roles: list) -> bool:
    return any(role in user_roles for role in roles)


class check_permissions:
    def __init__(self):
        pass

    async def __call__(self, resource: SystemFeature, request: Request, security_scopes: SecurityScopes):
        user: Optional[UserAuth] = await auth_scheme(request=request, security_scopes=security_scopes)
        method = request.method
        roles_scheme: Dict[str, list] = resource_permissions[resource]
        if user:
            user_roles = user.roles
            if verify_roles(roles=roles_scheme["required_roles"], user_roles=user_roles):
                return User(email=user.email)
            if verify_additional_rules(user_roles, method, roles_scheme["additional_rule"]):
                return User(email=user.email)
            raise UnauthorizedError("You don't have access to this endpoint")


#        authorization_header = request.headers.get("Authorization")
#        jwt = authorization_header.split(" ")[1] if authorization_header.startswith("Bearer") else None
#        if jwt:
#            try:
#                await jwt_verifier.verify_access_token(jwt)
#            except Exception as e:
#                raise UnauthorizedError()
#            _, claims, _, _ = jwt_verifier.parse_token(jwt)
#            user_roles = claims.get("roles", [])
#            email = claims.get("email", None)
#            id = claims.get("sub", None)
#            if verify_roles(roles=roles_scheme["required_roles"], user_roles=user_roles):
#                return User(id=id, email=email)
#            if verify_additional_rules(user_roles, method, roles_scheme["additional_rule"]):
#                return User(id=id, email=email)
#            raise UnauthorizedError("You don't have access to this endpoint")

class AuthenticatorSDK:

    @staticmethod
    def get_access_token():
        result = app_msal.acquire_token_for_client(scopes=auth_settings.SCOPE_DEFAULT)
        if "access_token" not in result:
            raise AuthenticationError
        return result["access_token"]

    async def list_users(self):
        async with httpx.AsyncClient() as client:
            token = self.get_access_token()
            response = await client.get(auth_settings.GROUP_URL, headers={"Authorization": f"Bearer {token}"})
            users_response: List[User] = []

            if response.status_code == 200:
                users = response.json()
                users_response.extend([User(email=user["mail"]) for user in users["value"]])
                while users.get("@odata.nextLink"):
                    response = await client.get(users.get("@odata.nextLink"),
                                                headers={"Authorization": f"Bearer {token}"})
                    users = response.json()
                    users_response.extend([User(email=user["mail"]) for user in users["value"]])

            return users_response
