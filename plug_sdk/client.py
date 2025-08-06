import asyncio
import json
import logging

from plug_sdk.legal_entity.schemas import (
    CompanyRequest,
    CompanyResponse,
    IndividualRequest,
    IndividualResponse,
)
from plug_sdk.policy.schemas import (
    BoletoRequest,
    BoletoResponse,
    InstallmentRequest,
    InstallmentResponse,
    IssuePolicyRequest,
    RejectProposalRequest,
    SubsidyLimitRequest,
    SubsidyLimitResponse,
    TransmissionRequest,
    TransmissionResponse,
)
from plug_sdk.sdk import PlugSDK
from plug_sdk.validations.schemas import (
    AddressSearchRequest,
    AddressSearchResponse,
    PostalCodeSearchRequest,
    PostalCodeSearchResponse,
    TechnicalRestrictionRequest,
    TechnicalRestrictionResponse,
)

logger = logging.getLogger("async_client")

logger.setLevel(logging.DEBUG)


async def transmit_quotation(plug: PlugSDK) -> TransmissionResponse:
    with open("transmit_quotation_request_data.json", "r") as f:
        request_data = json.load(f)

    request_data["data"]["section_number"] = 2
    del request_data["data"]["secao"]
    request_data["data"]["numeroProposta"] = str(int(request_data["data"]["numeroProposta"]) + 1)

    request = TransmissionRequest(**request_data)
    response: TransmissionResponse = await plug.transmit_quotation(request)
    return response


async def reject_proposal(plug: PlugSDK, proposal_id: int, free_text: str) -> TransmissionResponse:
    request = RejectProposalRequest(proposal_id=proposal_id, free_text=free_text)
    response: TransmissionResponse = await plug.reject_proposal(request)
    return response


async def issue_policy(plug: PlugSDK, proposal_id: int) -> TransmissionResponse:
    request = IssuePolicyRequest(proposal_id=proposal_id)
    response: TransmissionResponse = await plug.issue_policy(request)
    return response


async def get_subsidy_limit(plug: PlugSDK, cpf_cnpj: str, year: str) -> SubsidyLimitResponse:
    request = SubsidyLimitRequest(cpf_cnpj=cpf_cnpj, year=year)
    response: SubsidyLimitResponse = await plug.get_subsidy_limit(request)
    return response


async def get_boleto(plug: PlugSDK, policy_id: str, installment_number: str) -> BoletoResponse:
    request = BoletoRequest(policy_id=policy_id, installment_number=installment_number)
    response: BoletoResponse = await plug.get_boleto(request)
    return response


async def get_installment(plug: PlugSDK, installment_number: int, policy_id: str) -> InstallmentResponse:
    request = InstallmentRequest(installment_number=installment_number, policy_id=policy_id)
    response: InstallmentResponse = await plug.get_installment(request)
    return response


async def get_natural_person(plug: PlugSDK, cpf: str) -> IndividualResponse:
    request = IndividualRequest(cpf=cpf)
    response: IndividualResponse = await plug.get_natural_person(request)
    return response


async def get_legal_entity(plug: PlugSDK, cnpj: str) -> CompanyResponse:
    request = CompanyRequest(cnpj=cnpj)
    response: CompanyResponse = await plug.get_legal_entity(request)
    return response


async def search_postal_code(plug: PlugSDK, postal_code: str) -> PostalCodeSearchResponse:
    request = PostalCodeSearchRequest(postal_code=postal_code)
    response: PostalCodeSearchResponse = await plug.search_postal_code(request)
    return response


async def search_addres(plug: PlugSDK, state: str, city: str, street: str) -> AddressSearchResponse:
    request = AddressSearchRequest(state=state, city=city, street=street)
    response: AddressSearchResponse = await plug.search_address(request)
    return response


async def get_technical_restriction(plug: PlugSDK, cpf_cnpj: str, application: str) -> TechnicalRestrictionResponse:
    request = TechnicalRestrictionRequest(cpf_cnpj=cpf_cnpj, application=application)
    response: TechnicalRestrictionResponse = await plug.get_technical_restriction(request)
    return response


async def test_all(plug: PlugSDK):  # noqa: C901
    errors = {}
    responses = {}
    try:
        print("Transmitting quotation...")
        transmit_response = await transmit_quotation(plug)
        responses["transmit_quotation"] = transmit_response.model_dump(mode="json", by_alias=True)
    except Exception as e:
        errors["transmit_quotation"] = e

    try:
        print("Issuing policy...")
        issue_policy_response = await issue_policy(plug, proposal_id="10161564")
        responses["issue_policy"] = issue_policy_response.model_dump(mode="json", by_alias=True)
    except Exception as e:
        errors["issue_policy"] = e

    try:
        print("Rejecting proposal...")
        reject_proposal_response = await reject_proposal(plug, proposal_id="10161564", free_text="Nada a declarar")
        responses["reject_proposal"] = reject_proposal_response.model_dump(mode="json", by_alias=True)
    except Exception as e:
        errors["reject_proposal"] = e

    try:
        print("Getting subsidy limit...")
        get_subsidy_limit_response = await get_subsidy_limit(plug, cpf_cnpj="12345678909", year="2025")
        responses["get_subsidy_limit"] = get_subsidy_limit_response.model_dump(mode="json", by_alias=True)
    except Exception as e:
        errors["get_subsidy_limit"] = e

    try:
        print("Getting boleto...")
        get_boleto_response = await get_boleto(plug, policy_id="10165377", installment_number="1")
        responses["get_boleto"] = get_boleto_response.model_dump(mode="json", by_alias=True)
        del responses["get_boleto"]["boleto"]
    except Exception as e:
        errors["get_boleto"] = e

    try:
        print("Getting installment...")
        get_installment_response = await get_installment(plug, installment_number="1", policy_id="10165377")
        responses["get_installment"] = get_installment_response.model_dump(mode="json", by_alias=True)
    except Exception as e:
        errors["get_installment"] = e

    try:
        print("Getting natural person...")
        get_natural_person_response = await get_natural_person(plug, cpf="12345678909")
        responses["get_natural_person"] = get_natural_person_response.model_dump(mode="json", by_alias=True)
    except Exception as e:
        errors["get_natural_person"] = e

    try:
        print("Getting legal entity...")
        get_legal_entity_response = await get_legal_entity(plug, cnpj="49598227000170")
        responses["get_legal_entity"] = get_legal_entity_response.model_dump(mode="json", by_alias=True)
    except Exception as e:
        errors["get_legal_entity"] = e

    try:
        print("Getting postal code search...")
        search_postal_code_response = await search_postal_code(plug, postal_code="25555080")
        responses["search_postal_code"] = search_postal_code_response.model_dump(mode="json", by_alias=True)
    except Exception as e:
        errors["search_postal_code"] = e

    try:
        print("Getting address search...")
        search_address_response = await search_addres(plug, state="RJ", city="São João de Meriti", street="Rua das Flores")
        responses["search_address"] = search_address_response.model_dump(mode="json", by_alias=True)
    except Exception as e:
        errors["search_address"] = e

    try:
        print("Getting technical restriction...")
        get_technical_restriction_response = await get_technical_restriction(
            plug,
            cpf_cnpj="09976185740",
            application="agronext",
        )
        responses["get_technical_restriction"] = get_technical_restriction_response.model_dump(mode="json", by_alias=True)
    except Exception as e:
        errors["get_technical_restriction"] = e

    with open("responses.json", "w") as f:
        json.dump(responses, f, indent=4, default=str)

    if errors:
        with open("errors.log", "w") as f:
            for key, value in errors.items():
                f.write(f"{key}: {value}\n")


async def main(plug: PlugSDK):
    print("Getting address search...")
    response = await search_addres(plug, state="RS", city="Porto Alegre", street="Rua Otelo Rosa")
    # response = await search_postal_code(plug, postal_code="25555080")
    print(response)


if __name__ == "__main__":
    plug = PlugSDK(base_url="http://uatplug.essor.net/")
    asyncio.run(main(plug))
