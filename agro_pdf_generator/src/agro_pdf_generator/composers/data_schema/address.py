import agronext_procurement as procurement

from ...schemas import AddressData
from ...utils import (
    format_zip_code,
    text_or_default,
)


def build_address(
    view: procurement.ProposalView,
) -> AddressData:
    data = AddressData(
        zip_code="Não informado",
        country="Não informado",
        state="Não informado",
        city="Não informado",
        neighborhood="Não informado",
        street="Não informado",
        number="Não informado",
        complement="Não informado",
    )

    applicant = view.applicant
    if not applicant:
        return data

    mailing_address = applicant.contact_information.mailing_address
    if not mailing_address:
        return data

    data.street = text_or_default(mailing_address.street)
    data.number = text_or_default(mailing_address.number)
    data.neighborhood = text_or_default(mailing_address.neighborhood)
    data.zip_code = format_zip_code(mailing_address.postal_code)
    data.city = text_or_default(mailing_address.city)
    data.state = text_or_default(mailing_address.state)
    data.country = text_or_default(mailing_address.country)
    data.complement = text_or_default(mailing_address.complement)

    return data
