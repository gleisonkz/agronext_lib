import agronext_procurement_repositories as repositories

from ...schemas import AuthorizedPersonData


def build_proposal_authorized_persons(
    authorized_for_inspection: list[
        repositories.QuotationMetadata.InspectionAuthroizedMetadata
    ]
    | None,
) -> list[AuthorizedPersonData]:
    if not authorized_for_inspection:
        return []

    result: list[AuthorizedPersonData] = []
    for authorized in authorized_for_inspection:
        result.append(
            AuthorizedPersonData(
                name=authorized.name,
                social_name="",
                relationship=authorized.relationship,
                phone=authorized.phone,
            )
        )

    return result
