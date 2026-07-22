import agronext_procurement as procurement

from ...schemas import PropertyData
from ...utils import (
    format_coordinates,
    format_state,
    format_dms_coordinates,
    format_zip_code,
)


def build_property(
    view: procurement.ProposalView | procurement.QuotationView,
    municipality_code: str | None = None,
    *,
    for_policy: bool = False,
) -> PropertyData:
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
    if prop is None:
        return property_data

    property_data.name = prop.name or ""
    property_data.ownership_type = prop.ownership_type or ""

    address = prop.address
    if address is not None:
        property_data.street = address.street or ""
        property_data.number = address.number or ""
        property_data.neighborhood = address.neighborhood or ""
        property_data.city = address.city or ""
        property_data.state = address.state or ""
        property_data.country = address.country or ""

        property_data.zip_code = format_zip_code(address.postal_code or "") or ""

    location = prop.city_location
    if (
        location is not None
        and location.latitude is not None
        and location.longitude is not None
    ):
        property_data.coordinates = (
            format_dms_coordinates(location.latitude, location.longitude)
            if for_policy
            else f"{location.latitude},{location.longitude}"
        )

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
