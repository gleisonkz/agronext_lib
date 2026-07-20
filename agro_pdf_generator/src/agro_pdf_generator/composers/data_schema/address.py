import agronext_procurement as procurement

from ...schemas import AddressData
from ...utils import (
    format_address_line,
    format_city_state,
    format_zip_code,
    text_or_default,
)


def build_proposal_address(view: procurement.ProposalView) -> AddressData:
    address_data = AddressData(
        zip_code="Não informado",
        country="Não informado",
        state="Não informado",
        city="Não informado",
        neighborhood="Não informado",
        street="Não informado",
        number="Não informado",
        complement="Não informado",
    )

    if not view.applicant:
        return address_data

    mailing_address = view.applicant.contact_information.mailing_address
    if not mailing_address:
        return address_data

    address_data.zip_code = mailing_address.postal_code
    address_data.country = mailing_address.country
    address_data.state = mailing_address.state
    address_data.city = mailing_address.city
    address_data.neighborhood = mailing_address.neighborhood
    address_data.street = mailing_address.street
    address_data.number = mailing_address.number
    address_data.complement = mailing_address.complement or "Não informado"

    return address_data


def build_policy_insured_address(view: procurement.ProposalView) -> dict[str, str]:
    data = {
        "address": "Não informado",
        "neighborhood": "Não informado",
        "zip_code": "Não informado",
        "city_state": "Não informado",
    }

    applicant = getattr(view, "applicant", None)
    if not applicant:
        return data

    contact_information = getattr(applicant, "contact_information", None)
    mailing_address = getattr(contact_information, "mailing_address", None)
    if not mailing_address:
        return data

    data["address"] = format_address_line(
        getattr(mailing_address, "street", None),
        getattr(mailing_address, "number", None),
    )
    data["neighborhood"] = text_or_default(getattr(mailing_address, "neighborhood", None))
    data["zip_code"] = format_zip_code(getattr(mailing_address, "postal_code", None))
    data["city_state"] = format_city_state(
        getattr(mailing_address, "city", None),
        getattr(mailing_address, "state", None),
    )
    return data
