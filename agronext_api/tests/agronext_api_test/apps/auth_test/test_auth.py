import pytest
from agronext_api.apps.auth.profiles import Role, SystemFeature
from agronext_api.apps.auth.auth import check_permissions
from agronext_api.exceptions.auth import UnauthorizedError
def test_given_valids_user_when_call_check_permissions_return_user_or_exception(mocker):
    request = mocker.Mock()
    request.method = "GET"

    mock_user = mocker.Mock()

    mock_user.roles = [Role.TECHNICAL]
    check = check_permissions()

    user = check(resource=SystemFeature.GROUP_PROFILE_REGISTRATION,request=request, user=mock_user)

    assert user

    user = check(resource=SystemFeature.INSPECTION_COMPANY_REGISTRATION, request=request, user=mock_user)
    
    assert user

    with pytest.raises(UnauthorizedError, match="You don't have acces to this endpoint"):
        check(resource=SystemFeature.EXPENSE_LAUNCH, request=request, user=mock_user)
    