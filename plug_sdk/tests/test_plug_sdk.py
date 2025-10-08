import json
from unittest.mock import AsyncMock, patch

import pytest

from plug_sdk.financial import (
    BoletoResponse,
    CadinResponse,
    InstallmentResponse,
    SubsidyLimitResponse,
)
from plug_sdk.legal_identity import (
    BrokerResponse,
    LegalEntityResponse,
    NaturalPersonResponse,
)
from plug_sdk.notifications import EmailNotificationRequest, EmailNotificationResponse
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


@pytest.fixture(scope="module", autouse=True)
def mock_client():
    with patch("plug_sdk.sdk.BaseAsyncClient") as mock:
        mock.return_value.get = AsyncMock()
        mock.return_value.post = AsyncMock()
        yield mock


@pytest.fixture(scope="module")
def quotation_id() -> str:
    return "17599221588394"


@pytest.fixture(scope="module")
def proposal_id() -> str:
    return "123456"


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
    mock_client,
    sdk: PlugSDK,
    valid_transmission_data,
    proposal_id,
):
    mock_client.return_value.post.reset_mock()

    mock_client.return_value.post.return_value = SubmitQuotationResponse(
        codigoRetorno="0",
        mensagem="Sucesso",
        descricaoErro=None,
        idEndosso=proposal_id,
    )

    data = TransmissionData(**valid_transmission_data)
    response = await sdk.submit_quotation(data)
    assert isinstance(response, SubmitQuotationResponse)
    assert response.code == "0"
    assert response.proposal_id == proposal_id
    mock_client.return_value.post.assert_called_once()


@pytest.mark.asyncio
async def test_get_proposal(
    mock_client,
    sdk: PlugSDK,
    proposal_id,
    quotation_id,
):
    mock_client.return_value.get.reset_mock()

    mock_client.return_value.get.return_value = GetProposalResponse(
        cd_status=1,
        nm_status="Pendente",
        cd_proposta=quotation_id,
        id_endosso=proposal_id,
        cd_apolice=54321,
        id_apolice=88888,
        dt_emissao="2023-10-01T10:00:00",
    )

    response = await sdk.get_proposal(proposal_id)
    assert isinstance(response, GetProposalResponse)
    assert response.status_name == "Pendente"
    mock_client.return_value.get.assert_called_once()


@pytest.mark.asyncio
async def test_reject_proposal(mock_client, sdk: PlugSDK, proposal_id):
    mock_client.return_value.post.reset_mock()

    mock_client.return_value.post.return_value = RejectProposalResponse(codigoRetorno="0", mensagem="Proposta recusada com sucesso")

    response = await sdk.reject_proposal(
        proposal_id=proposal_id,
        description="Motivo de teste",
        motive_code=1,
    )
    assert isinstance(response, RejectProposalResponse)
    assert response.code == "0"
    mock_client.return_value.post.assert_called_once()


@pytest.mark.asyncio
async def test_issue_policy(
    mock_client,
    sdk: PlugSDK,
    proposal_id,
    policy_id,
):
    mock_client.return_value.post.reset_mock()
    mock_client.return_value.post.return_value = IssuePolicyResponse(
        codigoRetorno="0",
        mensagem="Apolice emitida com sucesso",
        numeroApolice=policy_id,
    )

    response = await sdk.issue_policy(proposal_id)
    assert response.policy_id == policy_id


@pytest.mark.asyncio
async def test_generate_document(
    mock_client,
    sdk: PlugSDK,
    proposal_id,
):
    mock_client.return_value.post.reset_mock()
    mock_client.return_value.post.return_value = PolicyDocumentResponse(
        report_base64_pdf="JVBERi0xLjQKJcfs... (truncated for brevity)",
    )

    response = await sdk.generate_policy_document(proposal_id=proposal_id)
    assert isinstance(response, PolicyDocumentResponse)
    assert response.report_base64_pdf.startswith("JVBERi0xLjQKJcfs")
    mock_client.return_value.post.assert_called_once()


@pytest.mark.asyncio
async def test_get_installments(
    mock_client,
    sdk: PlugSDK,
    quotation_id,
    proposal_id,
    policy_id,
    endorsement_number,
):
    mock_client.return_value.get.reset_mock()

    mock_client.return_value.get.return_value = InstallmentResponse(
        parcelas=[
            {
                "cd_proposta": quotation_id,
                "id_endosso": proposal_id,
                "cd_apolice": policy_id,
                "nr_endosso": endorsement_number,
                "nr_parcela": 1,
                "titulo": "Parcela 2/6 - Endosso",
                "situacao": "Pago",
                "dt_pagamento": "2025-09-15",
                "dt_baixa": "2025-09-17",
                "valor_recebido": "1250.50",
                "vl_tarifario": "1100.00",
                "vl_iof": "75.50",
                "vl_total": "1175.50",
                "dt_representacao": "2025-09-01",
                "dt_vencimento": "2025-09-10",
            }
        ]
    )

    response = await sdk.get_installments(policy_id=policy_id, installment=None)
    assert response.installments[0].total_amount == "1175.50"


@pytest.mark.asyncio
async def test_get_boleto(mock_client, sdk: PlugSDK, policy_id):
    mock_client.return_value.get.reset_mock()

    mock_client.return_value.get.return_value = BoletoResponse(
        policy_id=policy_id,
        installment_number=1,
        boleto_base64_pdf="JVBERi0xLjQKJcfs... (truncated for brevity)",
    )
    response = await sdk.get_boleto(policy_id=policy_id, installment=1)
    assert isinstance(response, BoletoResponse)
    mock_client.return_value.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_federal_subsidy_limit(mock_client, sdk: PlugSDK):
    mock_client.return_value.get.reset_mock()

    mock_client.return_value.get.return_value = SubsidyLimitResponse(
        **{
            "nrCpfCnpjSegurado": "12345678901",
            "nmSegurado": "João da Silva",
            "anPeriodoExercicio": "2025",
            "limitesSegurado": {
                "limiteSegurado": [
                    {
                        "dsModalidade": "Agrícola",
                        "vlSaldoComprometido": 50000.0,
                        "vlSaldoDisponivel": 150000.0,
                    },
                    {
                        "dsModalidade": "Pecuária",
                        "vlSaldoComprometido": 25000.0,
                        "vlSaldoDisponivel": 100000.0,
                    },
                ]
            },
        }
    )
    response = await sdk.get_federal_subsidy_limit(cpf_cnpj="10020020015", year=2025)
    assert isinstance(response, SubsidyLimitResponse)
    mock_client.return_value.get.assert_called_once()


@pytest.mark.asyncio
async def test_cadin_lookup(mock_client, sdk: PlugSDK):
    mock_client.return_value.get.reset_mock()

    mock_client.return_value.get.return_value = CadinResponse(
        **{
            "transacao": {
                "id": 101,
                "dataHoraExecucao": "2025-10-08T14:23:00",
                "status": "SUCESSO",
            },
            "segurado": {"nrCpfCnpjSegurado": "10020020015", "stPessoa": "REGULAR"},
        }
    )
    response = await sdk.cadin_lookup("10020020015")
    assert isinstance(response, CadinResponse)
    mock_client.return_value.get.assert_called_once()


@pytest.mark.asyncio
async def test_search_postal_code(mock_client, sdk: PlugSDK):
    mock_client.return_value.get.reset_mock()

    mock_client.return_value.get.return_value = AddressLookupResponse(
        **{
            "cep": "01001-000",
            "uf": "SP",
            "numeroLocalidade": 123,
            "localidade": "São Paulo",
            "logradouro": "Praça da Sé",
            "tipoLogradouro": "Praça",
            "nomeLogradouro": "Sé",
            "abreviatura": "Pça",
            "bairro": "Sé",
            "tipoCEP": 1,
            "lado": "Ímpar",
            "numeroInicial": 1,
            "numeroFinal": 999,
        }
    )
    response = await sdk.search_postal_code("01001-000")
    assert isinstance(response, AddressLookupResponse)
    mock_client.return_value.get.assert_called_once()


@pytest.mark.asyncio
async def test_search_address(mock_client, sdk: PlugSDK):
    mock_client.return_value.get.reset_mock()

    mock_client.return_value.get.return_value = AddressLookupResponse(
        **{
            "cep": "01001-000",
            "uf": "SP",
            "numeroLocalidade": 123,
            "localidade": "São Paulo",
            "logradouro": "Praça da Sé",
            "tipoLogradouro": "Praça",
            "nomeLogradouro": "Sé",
            "abreviatura": "Pça",
            "bairro": "Sé",
            "tipoCEP": 1,
            "lado": "Ímpar",
            "numeroInicial": 1,
            "numeroFinal": 999,
        }
    )
    response = await sdk.search_address("SP", "São Paulo", "Praça da Sé")
    assert isinstance(response, AddressLookupResponse)
    mock_client.return_value.get.assert_called_once()


@pytest.mark.asyncio
async def test_verify_technical_restriction(mock_client, sdk: PlugSDK):
    mock_client.return_value.get.reset_mock()

    mock_client.return_value.get.return_value = TechnicalRestrictionResponse(
        **{
            "cpfCnpj": "12345678901",
            "nome": "Maria Oliveira",
            "mensagem": "Restrição técnica identificada para o CPF informado.",
            "restricao": True,
        }
    )
    response = await sdk.verify_technical_restriction("10020020015")
    assert isinstance(response, TechnicalRestrictionResponse)
    mock_client.return_value.get.assert_called_once()


# @pytest.mark.asyncio
# async def test_get_broker_details(mock_client, sdk: PlugSDK):
#     mock_client.return_value.get.reset_mock()

# mock_client.return_value.get.return_value = BrokerResponse()
#     response = await sdk.get_broker_details("12345678901")
#     assert isinstance(response, BrokerResponse)
#     mock_client.return_value.get.assert_called_once()


# @pytest.mark.asyncio
# async def test_get_natural_person_details(mock_client, sdk: PlugSDK):
#     mock_client.return_value.get.reset_mock()

# mock_client.return_value.get.return_value = NaturalPersonResponse()
#     response = await sdk.get_natural_person_details("12345678901")
#     assert isinstance(response, NaturalPersonResponse)
#     mock_client.return_value.get.assert_called_once()


# @pytest.mark.asyncio
# async def test_get_legal_entity_details(mock_client, sdk: PlugSDK):
#     mock_client.return_value.get.reset_mock()

# mock_client.return_value.get.return_value = LegalEntityResponse()
#     response = await sdk.get_legal_entity_details("12345678000199")
#     assert isinstance(response, LegalEntityResponse)
#     mock_client.return_value.get.assert_called_once()


# @pytest.mark.asyncio
# async def test_send_email(mock_client, sdk: PlugSDK):
#     mock_client.return_value.post.reset_mock()

# mock_client.return_value.post.return_value = EmailNotificationResponse()
#     request = EmailNotificationRequest(
#         to="test@example.com", subject="Test Subject", body="Test Body"
#     )
#     response = await sdk.send_email("test@example.com", "Test Subject", request)
#     assert isinstance(response, EmailNotificationResponse)
#     mock_client.return_value.post.assert_called_once()
