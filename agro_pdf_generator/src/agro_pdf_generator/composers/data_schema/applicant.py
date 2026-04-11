import agronext_procurement as procurement

from ...schemas import ApplicantData
from agronext_procurement.value_objects.shared.contact_information import ContactInformation

def _format_phone(value: object | None) -> str:
    if value is None:
        return ""

    area_code = getattr(value, "area_code", None)
    number = getattr(value, "number", None)
    if number is None:
        return str(value)

    digits = "".join(char for char in str(number) if char.isdigit())
    local_number = digits[-9:] if len(digits) >= 9 else digits
    if len(local_number) > 4:
        formatted_number = f"{local_number[:5]}-{local_number[5:]}"
    else:
        formatted_number = local_number

    if area_code is not None:
        return f"({area_code}) {formatted_number}"
    return formatted_number


def _fill_contact_info(
    applicant_data: ApplicantData,
    contact_information: ContactInformation,
) -> None:
    applicant_data.main_email = contact_information.email or "Não informado"

    phone = contact_information.phones[0] if contact_information.phones else None
    applicant_data.phone_number = _format_phone(phone)
    applicant_data.phone_type = phone.type if phone is not None else ""
    applicant_data.is_whatsapp = "Sim" if phone and phone.is_whatsapp else "Não"


def build_applicant(view: procurement.QuotationView) -> ApplicantData:

    # Applicant
    applicant_data = ApplicantData(
        name="Não informado",
        cpf="Não informado",
        birth_date="Não informado",
        social_name="Não informado",
        document_number="Não informado",
        issuing_authority="Não informado",
        issue_date="Não informado",
        marital_status="Não informado",
        main_email="Não informado",
        phone_number="Não informado",
        phone_type="Não informado",
        is_whatsapp="Não informado",
        professional_category="Não informado",
        income="Não informado",
    )
    if isinstance(view.applicant, procurement.NPApplicantView):
        identity = view.applicant.identity

        applicant_data.name = identity.full_name
        applicant_data.marital_status = (
            identity.marital_status if identity.marital_status else "Não informado"
        )
        applicant_data.cpf = identity.cpf.number
        applicant_data.birth_date = identity.birth_date.strftime("%d/%m/%Y")
        applicant_data.social_name = identity.social_name or "Não informado"
        applicant_data.document_number = view.applicant.document_number
        applicant_data.professional_category = (
            identity.occupation.value if identity.occupation else "Não informado"
        )
        applicant_data.income = identity.income.value if identity.income else "Não informado"
        _fill_contact_info(applicant_data, view.applicant.contact_information)

        for doc in identity.additional_documents or []:
            if doc.type == procurement.DocumentTypes.RG:
                applicant_data.document_number = doc.number
                applicant_data.issuing_authority = doc.issuing_authority
                applicant_data.issue_date = doc.issue_date.strftime("%d/%m/%Y")

    elif isinstance(view.applicant, procurement.LEApplicantView):
        identity = view.applicant.identity

        applicant_data.name = identity.trade_name
        applicant_data.cpf = identity.cnpj.number
        applicant_data.document_number = view.applicant.document_number
        _fill_contact_info(applicant_data, view.applicant.contact_information)

    return applicant_data
