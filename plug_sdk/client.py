import asyncio
import json
import traceback

from pydantic_settings import BaseSettings, SettingsConfigDict

from plug_sdk.policy import (
    TransmissionData,
)
from plug_sdk.sdk import (
    Applications,
    DomainTypes,
    EmailTemplateTypes,
    PlugSDK,
    SearchIncludeOptions,
)
from plug_sdk.scap.schemas import Roles


async def test_submit_quotation(
    sdk: PlugSDK,
    valid_transmission_data,
):
    data = TransmissionData(**valid_transmission_data)
    return await sdk.submit_quotation(data)


async def test_get_proposal(
    sdk: PlugSDK,
    quotation_id,
):
    return await sdk.get_proposal(quotation_id)


async def test_reject_proposal(sdk: PlugSDK, proposal_id):
    return await sdk.reject_proposal(
        proposal_id=proposal_id,
        description="Motivo de teste",
        motive_code=1,
    )


async def test_issue_policy(
    sdk: PlugSDK,
    proposal_id,
):
    return await sdk.issue_policy(proposal_id)


async def test_generate_document(
    sdk: PlugSDK,
    proposal_id,
):
    return await sdk.generate_policy_document(proposal_id=proposal_id)


async def test_get_installments(
    sdk: PlugSDK,
    proposal_id,
):
    return await sdk.get_installments(proposal_id=proposal_id, installment=0)


async def test_get_boleto(sdk: PlugSDK, proposal_id, installment):
    return await sdk.get_boleto(proposal_id=proposal_id, installment=installment)


async def test_get_federal_subsidy_limit(sdk: PlugSDK, cpf_cnpj, year):
    return await sdk.get_federal_subsidy_limit(cpf_cnpj=cpf_cnpj, year=year)


async def test_cadin_lookup(sdk: PlugSDK, cpf_cnpj):
    return await sdk.cadin_lookup(cpf_cnpj=cpf_cnpj)


async def test_search_postal_code(sdk: PlugSDK, postal_code):
    return await sdk.search_postal_code(postal_code=postal_code)


async def test_search_address(sdk: PlugSDK, state, city, street):
    return await sdk.search_address(state=state, city=city, street=street)


async def test_verify_technical_restriction(sdk: PlugSDK, cpf_cnpj):
    return await sdk.verify_technical_restriction(cpf_cnpj=cpf_cnpj)


async def test_get_natural_person_details(sdk: PlugSDK, cpf: str):
    return await sdk.get_natural_person_details(cpf=cpf)


async def test_get_legal_entity_details(sdk: PlugSDK, cnpj: str):
    return await sdk.get_legal_entity_details(cnpj=cnpj)


async def test_send_email(sdk: PlugSDK):
    return await sdk.send_email(
        application=Applications.AGRONEXT,
        template=EmailTemplateTypes.EXTERNAL,
        subject="Test Email",
        description="Email sent via PlugSDK",
        body=[
            {
                "header": "Test Header",
                "body": "Test Body",
            }
        ],
        to=[
            {
                "name": "Test Recipient",
                "email": "cristovam.lage@essor.com.br",
            },
        ],
    )


def capture_response_error(func):
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            return result, None
        except Exception as e:
            traceback.print_exc()
            return None, f"{type(e).__name__}: {str(e)}"

    return wrapper


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    DEBUG: bool = True

    LOG_LEVEL: str = "INFO"

    PLUG_API_KEY: str = ""


async def main():
    settings = Settings()
    plug = PlugSDK(
        base_url="http://uatplug.essor.net/",
        credentials={"api_key": settings.PLUG_API_KEY},
    )

    with open("tests/fixtures/valid_transmission_data.json") as f:
        request_data = json.load(f)
        request_data["section_number"] = 2
        del request_data["secao"]
        request_data["numeroProposta"] = str(int(request_data["numeroProposta"]) + 10)

    with open("tests/fixtures/valid_transmission_response.json") as f:
        response_data = json.load(f)

    quotation_id = "17604470749248"  # request_data["numeroProposta"]
    proposal_id = int(response_data["idEndosso"])
    broker_cnpj = "08270601000126"
    policy_id = "xpto"
    cpf = "01368766099"
    cnpj = "14525684000150"
    year = 2025
    postal_code = "91760600"
    state = "RS"
    city = "Porto Alegre"
    street = "Ipiranga"
    installment = 1

    test_funcs = [
        {
            "name": "submit_quotation",
            "fn": test_submit_quotation,
            "params": {
                "sdk": plug,
                "valid_transmission_data": request_data,
            },
        },
        {
            "name": "get_proposal",
            "fn": test_get_proposal,
            "params": {"sdk": plug, "quotation_id": quotation_id},
        },
        {
            "name": "reject_proposal",
            "fn": test_reject_proposal,
            "params": {"sdk": plug, "proposal_id": proposal_id},
        },
        {
            "name": "issue_policy",
            "fn": test_issue_policy,
            "params": {
                "sdk": plug,
                "proposal_id": proposal_id,
            },
        },
        {
            "name": "generate_document",
            "fn": test_generate_document,
            "params": {"sdk": plug, "proposal_id": proposal_id},
        },
        {
            "name": "get_installments",
            "fn": test_get_installments,
            "params": {"sdk": plug, "proposal_id": proposal_id},
        },
        {
            "name": "get_boleto",
            "fn": test_get_boleto,
            "params": {
                "sdk": plug,
                "proposal_id": proposal_id,
                "installment": installment,
            },
        },
        {
            "name": "get_federal_subsidy_limit",
            "fn": test_get_federal_subsidy_limit,
            "params": {"sdk": plug, "cpf_cnpj": cpf, "year": year},
        },
        {
            "name": "cadin_lookup",
            "fn": test_cadin_lookup,
            "params": {"sdk": plug, "cpf_cnpj": cpf},
        },
        {
            "name": "search_postal_code",
            "fn": test_search_postal_code,
            "params": {"sdk": plug, "postal_code": postal_code},
        },
        {
            "name": "search_address",
            "fn": test_search_address,
            "params": {"sdk": plug, "state": state, "city": city, "street": street},
        },
        {
            "name": "verify_technical_restriction",
            "fn": test_verify_technical_restriction,
            "params": {"sdk": plug, "cpf_cnpj": cpf},
        },
        {
            "name": "get_natural_person_details",
            "fn": test_get_natural_person_details,
            "params": {"sdk": plug, "cpf": cpf},
        },
        {
            "name": "get_legal_entity_details",
            "fn": test_get_legal_entity_details,
            "params": {"sdk": plug, "cnpj": cnpj},
        },
        {
            "name": "get_broker_details",
            "fn": plug.get_broker_details,
            "params": {"cpf_cnpj": broker_cnpj},
        },
        {
            "name": "create_external_user",
            "fn": plug.create_external_user,
            "params": {
                "name": "Marcelo Paulino",
                "email": "mpaulino@scor.com",
                "phone": "+5551980125321",
            },
        },
        {
            "name": "filter_external_users",
            "fn": plug.filter_external_users,
            "params": {"email": "cristovam.lage@essor.com.br"},
        },
        {
            "name": "send_email",
            "fn": test_send_email,
            "params": {"sdk": plug},
        },
    ]

    domain_scap_funcs = [
        {
            "name": f"get_domain_{domain.value}",
            "fn": plug.list_domain_items,
            "params": {"domain": domain},
        }
        for domain in list(DomainTypes)
    ]

    scap_funcs = [
        {
            "name": "list_roles",
            "fn": plug.list_roles,
            "params": {},
        },
        {
            "name": "list_parties",
            "fn": plug.list_parties,
            "params": {
                "include": [
                    SearchIncludeOptions.ROLES,
                    SearchIncludeOptions.CONTACT,
                    SearchIncludeOptions.BANKING_DETAILS,
                    SearchIncludeOptions.ADDRESSES,
                    SearchIncludeOptions.DOCUMENTS,
                ],
                "document_number": "86908394026",
            },
        },
        {
            "name": "list_contacts",
            "fn": plug.list_contact_information,
            "params": {
                "contact": "raphael.luzo@essor.com.br",
                "include_person": True,
            },
        },
    ]

    test_skip_list = [
        "submit_quotation",
        "get_proposal",
        "reject_proposal",
        "issue_policy",
        "generate_document",
        "get_installments",
        "get_boleto",
        "get_federal_subsidy_limit",
        "cadin_lookup",
        "search_postal_code",
        "search_address",
        "verify_technical_restriction",
        "get_natural_person_details",
        "get_legal_entity_details",
        # "create_external_user",
        "filter_external_users",
        "send_email",
        "get_broker_details",
    ]
    scap_skip_list = [
        "list_roles",
        "list_parties",
        # "list_contacts",
    ]

    skip_list = test_skip_list + scap_skip_list

    responses = {}
    errors = {}

    for test in test_funcs:
        name = test["name"]

        if name in skip_list:
            print(f"⚠️ Skipping {name}")
            continue

        fn = test["fn"]
        params = test["params"]

        wrapped_fn = capture_response_error(fn)
        response, error = await wrapped_fn(**params)

        if error:
            errors[name] = error
        else:
            try:
                responses[name] = json.loads(json.dumps(response, default=str))
            except Exception as dump_err:
                errors[name] = f"Response not serializable: {dump_err}"

    result = {"responses": responses, "errors": errors}

    with open("test_run_output.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("✅ Done. Output saved to test_run_output.json")


async def create_broker_user():
    settings = Settings()
    plug = PlugSDK(
        base_url="http://uatplug.essor.net/",
        credentials={"api_key": settings.PLUG_API_KEY},
    )
    # response = await plug.list_parties(
    #     per_page=100,
    #     include=[
    #         SearchIncludeOptions.ROLES,
    #         # SearchIncludeOptions.DOCUMENTS,
    #         # SearchIncludeOptions.CONTACT,
    #     ],
    # )
    response = await plug.list_brokers(per_page=1, page=1)
    parties = response.data
    brokers = [p for p in parties if any(r.id == Roles.BROKER for r in p.roles)]
    broker = brokers[0] if brokers else None

    if broker:
        cnpj = broker.document_number
        email = "teste@teste.com"
        phone = "51997182626"
        name = "Teste External User"
        broker = await plug.get_legal_entity_details(cnpj=cnpj)
        user = await plug.create_external_user(email=email, phone=phone, name=name)
        print(f"User: {user.user_data.model_dump()}")


if __name__ == "__main__":
    asyncio.run(create_broker_user())
