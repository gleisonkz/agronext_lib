import agronext_procurement as procurement

from ...schemas import ApplicantData


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

        for doc in identity.additional_documents or []:
            if hasattr(doc, "issuing_authority") and getattr(doc, "issuing_authority"):
                applicant_data.issuing_authority = getattr(doc, "issuing_authority")
            if hasattr(doc, "issue_date") and getattr(doc, "issue_date"):
                applicant_data.issue_date = getattr(doc, "issue_date").strftime(
                    "%d/%m/%Y"
                )

    return applicant_data
