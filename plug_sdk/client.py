import json
import logging
import asyncio
from plug_sdk.sdk import PlugSDK
 
 
from plug_sdk.legal_entity.schemas import (
    IndividualRequest,
    IndividualResponse,
    CompanyRequest,
    CompanyResponse,
)
 
from plug_sdk.policy.schemas import (
    TransmissionRequest,
    TransmissionResponse,
    RejectProposalRequest,
    IssuePolicyRequest,
    InstallmentRequest,
    InstallmentResponse,
    BoletoRequest,
    BoletoResponse,
    SubsidyLimitRequest,
    SubsidyLimitResponse,
)
from plug_sdk.validations.schemas import (
    AddressLookupRequest,
    AddressLookupResponse,
    TechnicalRestrictionRequest,
    TechnicalRestrictionResponse,
)
 
logger = logging.getLogger("async_client")
 
logger.setLevel(logging.DEBUG)
 
 
async def transmit_quotation(plug: PlugSDK) -> TransmissionResponse:
    with open("transmit_quotation_request_data.json", "r") as f:
        request_data = json.load(f)

    request_data['data']['section_number'] = 2
    del request_data['data']['secao']
    request_data['data']["numeroProposta"] = str(int(request_data['data']["numeroProposta"]) + 1)

    request = TransmissionRequest(**request_data)
    response: TransmissionResponse = await plug.transmit_quotation(request)
    return response
 
 
async def reject_proposal(
    plug: PlugSDK, proposal_id: int, free_text: str
) -> TransmissionResponse:
    request = RejectProposalRequest(proposal_id=proposal_id, free_text=free_text)
    response: TransmissionResponse = await plug.reject_proposal(request)
    return response
 
 
async def issue_policy(plug: PlugSDK, proposal_id: int) -> TransmissionResponse:
    request = IssuePolicyRequest(proposal_id=proposal_id)
    response: TransmissionResponse = await plug.issue_policy(request)
    return response
 
 
async def get_subsidy_limit(
    plug: PlugSDK, cpf_cnpj: str, year: str
) -> SubsidyLimitResponse:
    request = SubsidyLimitRequest(cpf_cnpj=cpf_cnpj, year=year)
    response: SubsidyLimitResponse = await plug.get_subsidy_limit(request)
    return response
 
 
async def get_boleto(
    plug: PlugSDK, policy_id: str, installment_number: str
) -> BoletoResponse:
    request = BoletoRequest(
        policy_id=policy_id, installment_number=installment_number
    )
    response: BoletoResponse = await plug.get_boleto(request)
    return response
 
 
async def get_installment(
    plug: PlugSDK, installment_number: int, policy_id: str
) -> InstallmentResponse:
    request = InstallmentRequest(
        installment_number=installment_number, policy_id=policy_id
    )
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
 
 
async def get_address_lookup(plug: PlugSDK, postal_code: str) -> AddressLookupResponse:
    request = AddressLookupRequest(postal_code=postal_code)
    response: AddressLookupResponse = await plug.get_address_lookup(request)
    return response
 
 
async def get_technical_restriction(
    plug: PlugSDK, cpf_cnpj: str, application: str
) -> TechnicalRestrictionResponse:
    request = TechnicalRestrictionRequest(cpf_cnpj=cpf_cnpj, application=application)
    response: TechnicalRestrictionResponse = await plug.get_technical_restriction(
        request
    )
    return response
 
 
async def test_all(plug: PlugSDK):
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
        reject_proposal_response = await reject_proposal(
            plug, proposal_id="10161564", free_text="Nada a declarar"
        )
        responses["reject_proposal"] = reject_proposal_response.model_dump(mode="json", by_alias=True)
    except Exception as e:
        errors["reject_proposal"] = e

    try:
        print("Getting subsidy limit...")
        get_subsidy_limit_response = await get_subsidy_limit(
            plug, cpf_cnpj="12345678909", year="2025"
        )
        responses["get_subsidy_limit"] = get_subsidy_limit_response.model_dump(mode="json", by_alias=True)
    except Exception as e:
        errors["get_subsidy_limit"] = e

    try:
        print("Getting boleto...")
        get_boleto_response = await get_boleto(
            plug, policy_id="10165377", installment_number="1"
        )
        responses["get_boleto"] = get_boleto_response.model_dump(mode="json", by_alias=True)
        del responses["get_boleto"]["boleto"]
    except Exception as e:
        errors["get_boleto"] = e

    try:
        print("Getting installment...")
        get_installment_response = await get_installment(
            plug, installment_number="1", policy_id="10165377"
        )
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
        print("Getting address lookup...")
        get_address_lookup_response = await get_address_lookup(plug, postal_code="25555080")
        responses["get_address_lookup"] = get_address_lookup_response.model_dump(mode="json", by_alias=True)
    except Exception as e:
        errors["get_address_lookup"] = e

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
                


async def main():
    plug = PlugSDK(base_url="http://uatplug.essor.net/")
    errors = {}
    responses = {}
    try:
        print("Transmitting quotation...")
        transmit_response = await transmit_quotation(plug)
        responses["transmit_quotation"] = transmit_response.model_dump(mode="json", by_alias=True)
    except Exception as e:
        errors["transmit_quotation"] = e

    with open("responses.json", "w") as f:
        json.dump(responses, f, indent=4, default=str)

    if errors:
        with open("errors.log", "w") as f:
            for key, value in errors.items():
                f.write(f"{key}: {value}\n")

if __name__ == "__main__":
    asyncio.run(main())
