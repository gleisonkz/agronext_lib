import agronext_procurement as procurement

from ...schemas import PropertyData


def build_property(
    view: procurement.ProposalView | procurement.QuotationView,
    municipality_code: str | None = None,
) -> PropertyData:
    # Property
    property_data = PropertyData(
        name="",
        ownership_type="",
        coordinates="",
        zip_code="",
        country="",
        state="",
        city="",
        bacen_code=municipality_code or "",
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

def build_simulation_location(
    *,
    state: str,
    city: str,
    country: str | None,
    latitude: float,
    longitude: float,
) -> PropertyData:
    return PropertyData(
        state=_format_state(state),
        city=city,
        country=country or "Brasil",
        coordinates=_format_coordinates(latitude, longitude),
    )

def _format_coordinates(latitude: float, longitude: float) -> str:
    return f"{latitude:.6f}, {longitude:.6f}"

def _format_state(value: str | None) -> str:
    if not value:
        return ""

    state_code = value.strip().upper()
    if state_code in procurement.BrazilianStateDisplayNames.__members__:
        return procurement.BrazilianStateDisplayNames[state_code].value

    return value
