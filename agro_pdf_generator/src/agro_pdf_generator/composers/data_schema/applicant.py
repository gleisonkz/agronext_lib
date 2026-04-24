import agronext_procurement as procurement
from collections.abc import Sequence
from typing import Any

from ...schemas import ApplicantData
from agronext_procurement.value_objects.shared.contact_information import ContactInformation


_REVENUE_RANGE_LABELS = {
    procurement.RevenueRange.UP_TO_1_2M.value: "Até 1.200.000,00",
    procurement.RevenueRange.FROM_1_2M_TO_10_5M.value: "De 1.200.000,01 até 10.500.000,00",
    procurement.RevenueRange.FROM_10_5M_TO_60M.value: "De 10.500.000,01 até 60.000.000,00",
    procurement.RevenueRange.ABOVE_60M.value: "Acima de 60.000.000,00",
}


def _format_revenue_range(value: object | None) -> str:
    if value is None:
        return "Não informado"

    raw_value = getattr(value, "value", value)
    normalized = str(raw_value).strip()

    if not normalized:
        return "Não informado"

    return _REVENUE_RANGE_LABELS.get(normalized, normalized)

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


def _format_document_type(value: object | None) -> str:
    if value is None:
        return "Documento"

    raw_value = getattr(value, "value", value)
    normalized = str(raw_value).strip()
    if not normalized:
        return "Documento"

    try:
        return procurement.DocumentTypes(normalized).value
    except ValueError:
        normalized_upper = normalized.upper()
        for document_type in procurement.DocumentTypes:
            if (
                document_type.name == normalized_upper
                or document_type.value.upper() == normalized_upper
            ):
                return document_type.value

    return normalized


def _document_type_from_primary_document(document_number: object | None) -> str:
    digits = "".join(char for char in str(document_number or "") if char.isdigit())
    if len(digits) == 14:
        return procurement.DocumentTypes.CNPJ.value
    if len(digits) == 11:
        return procurement.DocumentTypes.CPF.value
    return "Documento"


def _select_preferred_document(documents: Sequence[Any] | None) -> Any | None:
    if not documents:
        return None

    rg_document = next(
        (
            document
            for document in documents
            if getattr(document, "type", None) == procurement.DocumentTypes.RG
        ),
        None,
    )
    return rg_document or documents[0]


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
        document_type="Não informado",
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
        business_activity="Não informado",
        annual_gross_revenue="Não informado",
        net_worth="Não informado",
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
        applicant_data.document_type = _document_type_from_primary_document(applicant_data.cpf)
        applicant_data.document_number = applicant_data.cpf
        applicant_data.professional_category = (
            identity.occupation.value if identity.occupation else "Não informado"
        )
        applicant_data.income = identity.income.value if identity.income else "Não informado"
        _fill_contact_info(applicant_data, view.applicant.contact_information)

        selected_document = _select_preferred_document(identity.additional_documents)
        if selected_document is not None:
            applicant_data.document_type = _format_document_type(selected_document.type)
            applicant_data.document_number = selected_document.number or "Não informado"
            applicant_data.issuing_authority = (
                selected_document.issuing_authority or "Não informado"
            )
            applicant_data.issue_date = (
                selected_document.issue_date.strftime("%d/%m/%Y")
                if selected_document.issue_date
                else "Não informado"
            )

    elif isinstance(view.applicant, procurement.LEApplicantView):
        identity = view.applicant.identity

        applicant_data.name = identity.trade_name
        applicant_data.cpf = identity.cnpj.number
        applicant_data.document_type = _document_type_from_primary_document(applicant_data.cpf)
        applicant_data.document_number = applicant_data.cpf
        applicant_data.business_activity = identity.business_activity or "Não informado"
        applicant_data.annual_gross_revenue = _format_revenue_range(identity.gross_revenue)
        applicant_data.net_worth = _format_revenue_range(identity.net_worth)
        _fill_contact_info(applicant_data, view.applicant.contact_information)

    return applicant_data
