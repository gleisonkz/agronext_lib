import agronext_procurement as procurement

from ...schemas import BeneficiaryData


def _format_birth_date(value: object) -> str:
    if hasattr(value, "strftime"):
        return value.strftime("%d/%m/%Y")
    return str(value) if value else ""


def _format_phone(value: object) -> str:
    #TODO: replace with the format phone from utils, test before opening PR
    if value is None:
        return ""

    area_code = getattr(value, "area_code", None)
    number = getattr(value, "number", None)

    formatted_number = ""
    if number is not None:
        digits = "".join(char for char in str(number) if char.isdigit())
        local_number = digits[-9:] if len(digits) >= 9 else digits
        formatted_number = f"{local_number[:5]}-{local_number[5:]}"

    if area_code is not None and number is not None:
        return f"({area_code}) {formatted_number}"
    if number is not None:
        return formatted_number
    return str(value)


def build_proposal_beneficiaries(
    beneficiaries: list[procurement.NPBeneficiaryView | procurement.LEBeneficiaryView]
    | None,
) -> list[BeneficiaryData]:
    if not beneficiaries:
        return []

    result = []
    for b in beneficiaries:
        if isinstance(b, procurement.NPBeneficiaryView):
            identity = b.identity
            name = identity.full_name
            cpf = identity.cpf.number
            birth_date = _format_birth_date(identity.birth_date)
            social_name = identity.social_name or "Não informado"
        else:
            identity = b.identity
            name = identity.trade_name
            cpf = identity.cnpj.number
            birth_date = "Não informado"
            social_name = "Não informado"

        email = b.contact_information.email
        phone = _format_phone(
            b.contact_information.phones[0] if b.contact_information.phones else None
        )
        percentage = b.benefit_percentage
        relationship = b.relationship_to_applicant

        result.append(
            BeneficiaryData(
                name=name,
                cpf=cpf,
                birth_date=birth_date,
                social_name=social_name,
                email=email or "Não informado",
                phone=phone,
                percentage=str(percentage) if percentage is not None else "Não informado",
                value="Não informado",  # TODO: determine what is this value
                relationship=relationship or "Não informado",
            )
        )
    return result
