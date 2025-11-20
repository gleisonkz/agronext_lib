import asyncio
import logging

from plug_sdk import PlugSDK

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("external_data_sources")


async def safe(coro, logger, label) -> dict | None:
    try:
        result = await coro
        logger.info(f"{label}: {result}")
        return result.model_dump()
    except Exception as e:
        logger.error(f"{label} failed: {e}", exc_info=True)
        return None


async def email_lookup(
    email: str,
    plug: PlugSDK,
    logger: logging.Logger = logger,
) -> dict:
    scap_info_email = await safe(
        plug.list_contact_information(
            contact_type_id=1,  # Email
            contact=email,
            include_person=True,
        ),
        logger,
        f"SCAP info for email {email}",
    )

    return scap_info_email


async def cpf_lookup(
    cpf: str,
    year: int,
    plug: PlugSDK,
    logger: logging.Logger = logger,
):
    # Create tasks explicitly — no dict, no meta-programming
    task_scap = asyncio.create_task(
        safe(
            plug.list_parties(
                document_number=cpf,
                include=[
                    "addresses",
                    "communications",
                    "bankAccounts",
                    "documents",
                    "roles",
                ],
            ),
            logger,
            f"SCAP info for CPF {cpf}",
        )
    )

    task_details = asyncio.create_task(
        safe(
            plug.get_natural_person_details(cpf),
            logger,
            f"Details for CPF {cpf}",
        )
    )

    task_technical = asyncio.create_task(
        safe(
            plug.verify_technical_restriction(cpf),
            logger,
            f"Technical restrictions for CPF {cpf}",
        )
    )

    task_cadin = asyncio.create_task(
        safe(
            plug.cadin_lookup(cpf),
            logger,
            f"CADIN lookup for CPF {cpf}",
        )
    )

    task_subsidy = asyncio.create_task(
        safe(
            plug.get_federal_subsidy_limit(cpf, year),
            logger,
            f"Federal subsidy limit for CPF {cpf} in {year}",
        )
    )

    # Non-blocking parallel wait
    scap_info, details, technical_restrictions, cadin, federal_subsidy_limit = await asyncio.gather(
        task_scap,
        task_details,
        task_technical,
        task_cadin,
        task_subsidy,
    )

    return {
        "scap_info": scap_info,
        "details": details,
        "technical_restrictions": technical_restrictions,
        "cadin": cadin,
        "federal_subsidy_limit": federal_subsidy_limit,
    }


async def cnpj_lookup(
    cnpj: str,
    year: int,
    plug: PlugSDK,
    logger: logging.Logger = logger,
) -> dict:
    # Create tasks explicitly — no dict, no meta-programming
    task_scap = asyncio.create_task(
        safe(
            plug.list_parties(
                document_number=cnpj,
                include=[
                    "addresses",
                    "communications",
                    "bankAccounts",
                    "documents",
                    "roles",
                ],
            ),
            logger,
            f"SCAP info for CNPJ {cnpj}",
        )
    )

    task_details = asyncio.create_task(
        safe(
            plug.get_legal_entity_details(cnpj),
            logger,
            f"Details for CNPJ {cnpj}",
        )
    )

    task_technical = asyncio.create_task(
        safe(
            plug.verify_technical_restriction(cnpj),
            logger,
            f"Technical restrictions for CNPJ {cnpj}",
        )
    )

    task_cadin = asyncio.create_task(
        safe(
            plug.cadin_lookup(cnpj),
            logger,
            f"CADIN lookup for CNPJ {cnpj}",
        )
    )

    task_subsidy = asyncio.create_task(
        safe(
            plug.get_federal_subsidy_limit(cnpj, year),
            logger,
            f"Federal subsidy limit for CNPJ {cnpj} in {year}",
        )
    )

    # Non-blocking parallel wait
    scap_info, details, technical_restrictions, cadin, federal_subsidy_limit = await asyncio.gather(
        task_scap,
        task_details,
        task_technical,
        task_cadin,
        task_subsidy,
    )

    return {
        "scap_info": scap_info,
        "details": details,
        "technical_restrictions": technical_restrictions,
        "cadin": cadin,
        "federal_subsidy_limit": federal_subsidy_limit,
    }


async def main() -> str:
    ### === RUNTIME SETUP === ###
    PLUG_URL = "http://uatplug.essor.net/"

    plug = PlugSDK(base_url=PLUG_URL, credentials={"api_key": "XXU2YDUcRhxJqXWwPkMyW7JA5Kba3T1CIj9EZo6S4d44a7ce"})

    email = "raphael.luzo@essor.com.br"
    cpf = "71166763099"
    cpf = "01368766099"
    cnpj = "40929384000146"
    year = 2025

    email_result = await email_lookup(email, plug, logger)

    cpf_result = await cpf_lookup(cpf, year, plug, logger)

    cnpj_result = await cnpj_lookup(cnpj, year, plug, logger)


if __name__ == "__main__":
    asyncio.run(main())
