import pytest
from agronext_api.apps.auth.profiles import Role, SystemFeature
from agronext_api.apps.auth.auth import check_permissions
from agronext_api.exceptions.auth import UnauthorizedError
from agronext_api.apps.auth.auth import AuthenticatorSDK


@pytest.mark.asyncio
async def test_given_valids_user_when_call_check_permissions_return_user_or_exception(
    mocker,
):
    request = mocker.Mock()
    request.method = "GET"
    mock_user = mocker.Mock()
    mock_user.roles = [Role.TECHNICAL]
    mock_user.email = "email-teste@essor.com.br"
    mock_schema = mocker.patch(
        "agronext_api.apps.auth.auth.auth_scheme",
        new_callable=mocker.AsyncMock,
        return_value=mock_user,
    )
    scopes_mock = mocker.Mock()
    mock_schema.return_value = mock_user
    check = check_permissions()

    user = await check(
        resource=SystemFeature.GROUP_PROFILE_REGISTRATION,
        request=request,
        security_scopes=scopes_mock,
    )

    assert user

    user = await check(
        resource=SystemFeature.INSPECTION_COMPANY_REGISTRATION,
        request=request,
        security_scopes=scopes_mock,
    )

    assert user

    with pytest.raises(UnauthorizedError, match="You don't have access to this endpoint"):
        await check(
            resource=SystemFeature.EXPENSE_LAUNCH,
            request=request,
            security_scopes=scopes_mock,
        )


@pytest.mark.asyncio
async def test_given_succes_token_when_call_lisT_users_return_list_of_users():
    sdk = AuthenticatorSDK()
    users = await sdk.list_users()
    assert isinstance(users, list)
    assert len(users) > 0
