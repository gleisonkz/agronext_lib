import agronext_procurement as procurement

from ...schemas import AddressData


def build_proposal_address(view: procurement.ProposalView) -> AddressData:
    address_data = AddressData(
        zip_code="",
        country="",
        state="",
        city="",
        neighborhood="",
        street="",
        number="",
        complement="",
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
    address_data.complement = mailing_address.complement or ""

    return address_data
