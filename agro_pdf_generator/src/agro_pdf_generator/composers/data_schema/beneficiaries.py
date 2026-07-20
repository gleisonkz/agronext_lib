import agronext_procurement as procurement

from ...schemas import BeneficiaryData
from ...utils import (
    format_address_line,
    format_city_state,
    format_date_br,
    format_document_number,
    format_percentage,
    format_phone,
    format_zip_code,
    text_or_default,
)


def build_proposal_beneficiaries(
    beneficiaries: list[procurement.NPBeneficiaryView | procurement.LEBeneficiaryView]
    | None,
) -> list[BeneficiaryData]:
    if not beneficiaries:
        return []

    result = []
    for b in beneficiaries:
        if isinstance(b, procurement.NPBeneficiaryView):
            identity = b.identity
            name = identity.full_name
            cpf = identity.cpf.number
            birth_date = format_date_br(identity.birth_date)
            social_name = identity.social_name or "Não informado"
        else:
            identity = b.identity
            name = identity.trade_name
            cpf = identity.cnpj.number
            birth_date = "Não informado"
            social_name = "Não informado"

        email = b.contact_information.email
        phone = (
            format_phone(phone=b.contact_information.phones[0])
            if b.contact_information.phones
            else ""
        )
        percentage = b.benefit_percentage
        relationship = b.relationship_to_applicant

        result.append(
            BeneficiaryData(
                name=name,
                cpf=cpf,
                birth_date=birth_date,
                social_name=social_name,
                email=email or "Não informado",
                phone=phone,
                percentage=str(percentage) if percentage is not None else "Não informado",
                value="Não informado",  # TODO: determine what is this value
                relationship=relationship or "Não informado",
            )
        )
    return result


def build_policy_primary_beneficiary(
    beneficiaries: list[procurement.NPBeneficiaryView | procurement.LEBeneficiaryView] | None,
) -> dict[str, str]:
    result = {
        "name": "Não informado",
        "document": "Não informado",
        "share": "100%",
    }

    if not beneficiaries:
        return result

    first = beneficiaries[0]
    if isinstance(first, procurement.NPBeneficiaryView):
        result["name"] = first.identity.full_name or "Não informado"
    else:
        result["name"] = first.identity.trade_name or "Não informado"

    result["document"] = format_document_number(first.document_number)
    try:
        share = float(first.benefit_percentage) if first.benefit_percentage is not None else 100.0
    except (TypeError, ValueError):
        share = 100.0

    result["share"] = format_percentage(value=share)
    return result


def build_policy_beneficiaries(
    beneficiaries: list[procurement.NPBeneficiaryView | procurement.LEBeneficiaryView] | None,
) -> list[BeneficiaryData]:
    if not beneficiaries:
        return []

    result: list[BeneficiaryData] = []
    for beneficiary in beneficiaries:
        if isinstance(beneficiary, procurement.NPBeneficiaryView):
            name = beneficiary.identity.full_name or "Não informado"
            social_name = beneficiary.identity.social_name or "Não informado"
        else:
            name = beneficiary.identity.trade_name or "Não informado"
            social_name = "Não informado"

        mailing_address = getattr(
            getattr(beneficiary, "contact_information", None),
            "mailing_address",
            None,
        )

        address = format_address_line(
            getattr(mailing_address, "street", None),
            getattr(mailing_address, "number", None),
        )
        neighborhood = text_or_default(getattr(mailing_address, "neighborhood", None))
        city_state = format_city_state(
            getattr(mailing_address, "city", None),
            getattr(mailing_address, "state", None),
        )
        zip_code = format_zip_code(getattr(mailing_address, "postal_code", None))

        try:
            share = (
                str(beneficiary.benefit_percentage)
                if beneficiary.benefit_percentage is not None
                else "0"
            )
        except (TypeError, ValueError):
            share = "0"

        result.append(
            BeneficiaryData(
                name=name,
                cpf=format_document_number(beneficiary.document_number),
                social_name=social_name,
                address=address,
                neighborhood=neighborhood,
                city_state=city_state,
                zip_code=zip_code,
                percentage=share,
            )
        )

    return result
