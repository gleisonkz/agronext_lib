import functools

import msal
from fastapi_azure_auth import SingleTenantAzureAuthorizationCodeBearer
from fastapi_azure_auth.user import User
from fastapi import Request, Depends
from .auth_settings import auth_settings
from ...exceptions.auth import AuthenticationError, UnauthorizedError
from .profiles import resource_permissions, SystemFeature
from typing import Dict, List
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


def verify_additional_rules(user_roles, method, additional_roles: List[Dict[str, list]]) -> bool:
    for additional_role in additional_roles:
        methods = additional_role.get("methods", [])
        return any(role in user_roles for role in additional_role.get("roles", [])) and method in methods


class check_permissions:
    def __init__(self):
        pass

    def __call__(self, resource: SystemFeature, request: Request, user: User = Depends(auth_scheme)):
        method = request.method

        roles_scheme: Dict[str, list] = resource_permissions[resource]
        user_roles = user.roles
        if any(role in user_roles for role in roles_scheme["required_roles"]):
            return user
        if verify_additional_rules(user_roles, method, roles_scheme["additional_rule"]):
            return user
        raise UnauthorizedError("You don't have acces to this endpoint")


class AuthenticatorSDK:

    def get_access_token(self):
        result = app_msal.acquire_token_for_client(scopes=auth_settings.SCOPE_DEFAULT)
        if "access_token" not in result:
            raise AuthenticationError
        return result["access_token"]

    async def list_users(self):
        async with httpx.AsyncClient() as client:
            token = self.get_access_token()
            response = await client.get(auth_settings.GRAPH_URL, headers={"Authorization": f"Bearer {token}"})
            users = []
            # TODO Fazer a transformção do response em users
            if response.status_code == 200:
                #users = response.json()
                #for user in users['value']:
                #    t = {"name": user['displayName'], "email": user['mail']}
                #    userss.append(t)
                #while (users.get("@odata.nextLink")):
                #    response = await client.get(users.get("@odata.nextLink"),
                #                                headers={"Authorization": f"Bearer {token}"})
                #    users = response.json()
                #    for user in users['value']:
                #        t = {"name": user['displayName'], "email": user['mail']}
                #        userss.append(t)
                pass
            else:
                pass
                #print(f"Erro: {response.status_code}")

            return users
