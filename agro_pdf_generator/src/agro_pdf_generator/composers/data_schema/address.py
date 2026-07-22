import agronext_procurement as procurement

from ...schemas import AddressData
from ...utils import (
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


def build_policy_insured_address(view: procurement.ProposalView) -> AddressData:
    data = AddressData(
        zip_code="Não informado",
        country="",
        state="",
        city="",
        neighborhood="Não informado",
        street="",
        number="",
        complement="Não informado",
    )

    applicant = view.applicant
    if not applicant:
        return data

    contact_information = applicant.contact_information
    mailing_address = contact_information.mailing_address
    if not mailing_address:
        return data

    data.street = mailing_address.street or ""
    data.number = mailing_address.number or ""
    data.neighborhood = text_or_default(mailing_address.neighborhood)
    data.zip_code = format_zip_code(mailing_address.postal_code)
    data.city = mailing_address.city or ""
    data.state = mailing_address.state or ""
    data.country = mailing_address.country or ""
    data.complement = text_or_default(mailing_address.complement)

    return data
