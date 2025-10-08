import json

import pytest

from plug_sdk.financial import (
    BoletoResponse,
    CadinResponse,
    InstallmentResponse,
    SubsidyLimitResponse,
)
from plug_sdk.policy import (
    GetProposalResponse,
    IssuePolicyResponse,
    PolicyDocumentResponse,
    RejectProposalResponse,
    SubmitQuotationResponse,
    TransmissionData,
)
from plug_sdk.sdk import PlugSDK
from plug_sdk.validations import (
    AddressLookupResponse,
    TechnicalRestrictionResponse,
)


@pytest.fixture(scope="module")
def valid_transmission_data():
    with open("tests/fixtures/valid_transmission_data.json") as f:
        request_data = json.load(f)
    request_data["section_number"] = 2
    del request_data["secao"]
    request_data["numeroProposta"] = str(int(request_data["numeroProposta"]) + 1)
    return request_data


@pytest.fixture(scope="module")
def quotation_id() -> str:
    return "17599221588394"


@pytest.fixture(scope="module")
def proposal_id() -> str:
    return "10175986"


@pytest.fixture(scope="module")
def policy_id() -> str:
    return "123456"


@pytest.fixture(scope="module")
def endorsement_number() -> int:
    return 0


@pytest.fixture(scope="module")
def sdk():
    return PlugSDK(base_url="http://uatplug.essor.net/")


@pytest.mark.asyncio
async def test_submit_quotation(
    sdk: PlugSDK,
    valid_transmission_data,
):
    data = TransmissionData(**valid_transmission_data)
    response = await sdk.submit_quotation(data)
    assert isinstance(response, SubmitQuotationResponse)
    assert response.code == "0"


@pytest.mark.asyncio
async def test_get_proposal(
    sdk: PlugSDK,
    proposal_id,
):
    response = await sdk.get_proposal(proposal_id)
    assert isinstance(response, GetProposalResponse)
    assert response.status_name == "Emitida"


@pytest.mark.asyncio
async def test_reject_proposal(sdk: PlugSDK, proposal_id):
    response = await sdk.reject_proposal(
        proposal_id=proposal_id,
        description="Motivo de teste",
        motive_code=1,
    )
    assert isinstance(response, RejectProposalResponse)
    assert response.code == "0"


@pytest.mark.asyncio
async def test_issue_policy(
    sdk: PlugSDK,
    proposal_id,
    policy_id,
):
    response = await sdk.issue_policy(proposal_id)
    assert response.policy_id == policy_id


@pytest.mark.asyncio
async def test_generate_document(
    sdk: PlugSDK,
    proposal_id,
):
    response = await sdk.generate_policy_document(proposal_id=proposal_id)
    assert isinstance(response, PolicyDocumentResponse)
    assert response.report_base64_pdf.startswith("JVBERi0xLjQKJcfs")


@pytest.mark.asyncio
async def test_get_installments(
    sdk: PlugSDK,
    policy_id,
):
    response = await sdk.get_installments(policy_id=policy_id, installment=None)
    assert response.installments[0].total_amount == "1175.50"


@pytest.mark.asyncio
async def test_get_boleto(sdk: PlugSDK, policy_id):
    response = await sdk.get_boleto(policy_id=policy_id, installment=1)
    assert isinstance(response, BoletoResponse)


@pytest.mark.asyncio
async def test_get_federal_subsidy_limit(sdk: PlugSDK):
    response = await sdk.get_federal_subsidy_limit(cpf_cnpj="10020020015", year=2025)
    assert isinstance(response, SubsidyLimitResponse)


@pytest.mark.asyncio
async def test_cadin_lookup(sdk: PlugSDK):
    response = await sdk.cadin_lookup("10020020015")
    assert isinstance(response, CadinResponse)


@pytest.mark.asyncio
async def test_search_postal_code(sdk: PlugSDK):
    response = await sdk.search_postal_code("01001-000")
    assert isinstance(response, AddressLookupResponse)


@pytest.mark.asyncio
async def test_search_address(sdk: PlugSDK):
    response = await sdk.search_address("SP", "São Paulo", "Praça da Sé")
    assert isinstance(response, AddressLookupResponse)


@pytest.mark.asyncio
async def test_verify_technical_restriction(sdk: PlugSDK):
    response = await sdk.verify_technical_restriction("10020020015")
    assert isinstance(response, TechnicalRestrictionResponse)
