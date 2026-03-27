import agronext_procurement as procurement

from ...schemas import PropertyData


def build_quotation_property(view: procurement.QuotationView) -> PropertyData:
    # Property
    property_data = PropertyData(
        name="",
        ownership_type="",
        coordinates="",
        zip_code="",
        country="",
        state="",
        city="",
        bacen_code="",
        neighborhood="",
        street="",
        number="",
    )
    prop = view.properties[0] if view.properties else None
    if prop:
        property_data.name = prop.name
        property_data.ownership_type = prop.ownership_type
        property_data.coordinates = f"{prop.city_location.latitude},{prop.city_location.longitude}"
        property_data.zip_code = prop.address.postal_code
        property_data.country = prop.address.country
        property_data.state = prop.address.state
        property_data.city = prop.address.city
        property_data.neighborhood = prop.address.neighborhood
        property_data.street = prop.address.street
        property_data.number = prop.address.number

    return property_data


def build_proposal_property(view: procurement.ProposalView) -> PropertyData:
    # Property
    property_data = PropertyData(
        name="",
        ownership_type="",
        coordinates="",
        zip_code="",
        country="",
        state="",
        city="",
        bacen_code="",
        neighborhood="",
        street="",
        number="",
    )
    prop = view.properties[0] if view.properties else None
    if prop:
        property_data.name = prop.name
        property_data.ownership_type = prop.ownership_type
        property_data.coordinates = f"{prop.city_location.latitude},{prop.city_location.longitude}"
        property_data.zip_code = prop.address.postal_code
        property_data.country = prop.address.country
        property_data.state = prop.address.state
        property_data.city = prop.address.city
        property_data.neighborhood = prop.address.neighborhood
        property_data.street = prop.address.street
        property_data.number = prop.address.number

    return property_data