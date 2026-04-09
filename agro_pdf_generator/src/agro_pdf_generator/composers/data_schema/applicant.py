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
    applicant_data.main_email = contact_information.email or ""

    phone = contact_information.phones[0] if contact_information.phones else None
    applicant_data.phone_number = _format_phone(phone)
    applicant_data.phone_type = phone.type if phone is not None else ""
    applicant_data.is_whatsapp = "Sim" if phone and phone.is_whatsapp else "Não"


def build_applicant(view: procurement.QuotationView) -> ApplicantData:

    # Applicant
    applicant_data = ApplicantData(
        name="",
        cpf="",
        birth_date="",
        social_name="Não informado",
        document_number="",
        issuing_authority="",
        issue_date="",
        marital_status="",
        main_email="",
        phone_number="",
        phone_type="",
        is_whatsapp="",
        professional_category="",
        income="",
    )
    if isinstance(view.applicant, procurement.NPApplicantView):
        identity = view.applicant.identity

        applicant_data.name = identity.full_name
        applicant_data.marital_status = (
            identity.marital_status if identity.marital_status else ""
        )
        applicant_data.cpf = identity.cpf.number
        applicant_data.birth_date = identity.birth_date.strftime("%d/%m/%Y")
        applicant_data.social_name = identity.social_name or ""
        applicant_data.document_number = view.applicant.document_number
        applicant_data.professional_category = (
            identity.occupation.value if identity.occupation else ""
        )
        applicant_data.income = identity.income.value if identity.income else ""
        _fill_contact_info(applicant_data, view.applicant.contact_information)

        for doc in identity.additional_documents or []:
            if hasattr(doc, "issuing_authority") and getattr(doc, "issuing_authority"):
                applicant_data.issuing_authority = getattr(doc, "issuing_authority")
            if hasattr(doc, "issue_date") and getattr(doc, "issue_date"):
                applicant_data.issue_date = getattr(doc, "issue_date").strftime(
                    "%d/%m/%Y"
                )
    elif isinstance(view.applicant, procurement.LEApplicantView):
        identity = view.applicant.identity

        applicant_data.name = identity.trade_name
        applicant_data.cpf = identity.cnpj.number
        applicant_data.document_number = view.applicant.document_number
        _fill_contact_info(applicant_data, view.applicant.contact_information)

    return applicant_data
