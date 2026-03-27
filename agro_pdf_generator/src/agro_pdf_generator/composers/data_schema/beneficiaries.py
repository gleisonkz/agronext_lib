import agronext_procurement as procurement

from ...schemas import BeneficiaryData


def build_proposal_beneficiaries(
    beneficiaries: list[procurement.NPBeneficiaryView | procurement.LEBeneficiaryView]
    | None,
) -> list[BeneficiaryData]:
    if not beneficiaries:
        return []

    result = []
    for b in beneficiaries:
        # Defensive: some fields may not exist on both NP and LE types
        identity = b.identity

        name = identity.full_name
        cpf = identity.cpf
        birth_date = identity.birth_date
        if hasattr(birth_date, "strftime"):
            birth_date = birth_date.strftime("%d/%m/%Y")
        social_name = identity.social_name

        email = b.contact_information.email
        phone = b.contact_information.phones[0] if b.contact_information.phones else ""
        percentage = b.benefit_percentage
        relationship = b.relationship_to_applicant

        result.append(
            BeneficiaryData(
                name=name,
                cpf=cpf,
                birth_date=birth_date or "",
                social_name=social_name or "",
                email=email,
                phone=phone,
                percentage=str(percentage) if percentage is not None else "",
                value="",  # TODO: determine what is this value
                relationship=relationship,
            )
        )
    return result
