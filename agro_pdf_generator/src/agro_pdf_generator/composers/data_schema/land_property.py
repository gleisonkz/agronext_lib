import agronext_procurement as procurement

from ...schemas import PropertyData
from ...utils import (
    format_coordinates,
    format_state,
    format_address_line,
    format_city_state,
    format_dms_coordinates,
    format_zip_code,
)


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

def build_simulation_property(
    *,
    state: str,
    city: str,
    country: str | None,
    latitude: float,
    longitude: float,
) -> PropertyData:
    return PropertyData(
        state=format_state(state),
        city=city,
        country=country or "Brasil",
        coordinates=format_coordinates(latitude, longitude),
    )


def build_policy_property(
    view: procurement.ProposalView,
    municipality_code: str | None = None,
) -> dict[str, str]:
    data = {
        "address": "Não informado",
        "neighborhood": "Não informado",
        "zip_code": "Não informado",
        "city_state": "Não informado",
        "bacen_code": municipality_code or "Não informado",
        "name": "Não informado",
        "coordinates": "Não informado",
    }

    prop = view.properties[0] if view.properties else None
    if prop is None:
        return data

    data["name"] = prop.name or "Não informado"

    address = getattr(prop, "address", None)
    if address is not None:
        data["address"] = format_address_line(
            getattr(address, "street", None),
            getattr(address, "number", None),
        )
        data["neighborhood"] = getattr(address, "neighborhood", None) or "Não informado"
        data["zip_code"] = format_zip_code(getattr(address, "postal_code", None))
        data["city_state"] = format_city_state(
            getattr(address, "city", None),
            getattr(address, "state", None),
        )

    location = getattr(prop, "city_location", None)
    latitude = getattr(location, "latitude", None)
    longitude = getattr(location, "longitude", None)
    if latitude is not None and longitude is not None:
        data["coordinates"] = format_dms_coordinates(latitude, longitude)

    return data
