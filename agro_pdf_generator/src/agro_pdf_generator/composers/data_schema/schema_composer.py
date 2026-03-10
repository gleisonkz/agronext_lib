import agronext_procurement as procurement
import agronext_procurement_repositories as repositories

from ...schemas import PDFData
from .acceptance import build_quotation_acceptance
from .applicant import build_quotation_applicant
from .available_documents import build_quotation_available_documents
from .broker import build_quotation_broker
from .coordinates import build_quotation_coordinates
from .coverage import build_quotation_coverage
from .coverage_restrictions import build_quotation_coverage_restrictions
from .excluded_risks import build_quotation_excluded_risks
from .grace_period import build_quotation_grace_period
from .header import build_quotation_header
from .land_property import build_quotation_property
from .payment import build_quotation_payment
from .risk_data import build_quotation_risk_data
from .risk_questionnaire import build_quotation_risk_questionnaire
from .notifications import build_proponent_notifications
from .declarations import build_declarations


def build_quotation_data_from_domain(
    view: procurement.QuotationView,
    metadata: repositories.QuotationMetadata,
    broker_details: dict,
    croqui_bytes: bytes,
) -> PDFData:
    coverage = view.coverages[0].coverage if view.coverages else None
    financials = coverage.financials if coverage else None

    header_data = build_quotation_header(view, metadata, coverage)
    applicant_data = build_quotation_applicant(view)

    coverage_data = build_quotation_coverage(view, coverage)
    broker_data = build_quotation_broker(broker_details)
    payment_data = build_quotation_payment(
        metadata=metadata,
        financials=financials,
        broker_data=broker_data,
        coverage_data=coverage_data,
    )

    property_data = build_quotation_property(view)
    risk_data = build_quotation_risk_data(view.properties, financials)
    coords_data = build_quotation_coordinates(view.properties)
    risk_questionnaire_data = build_quotation_risk_questionnaire(metadata)
    acceptance_data = build_quotation_acceptance()
    grace_period_data = build_quotation_grace_period()
    coverage_restrictions_data = build_quotation_coverage_restrictions()
    available_documents_data = build_quotation_available_documents(
        ["101 - Granizo (Pêra)"]
    )
    excluded_risks_data = build_quotation_excluded_risks()
    notifications_data = build_proponent_notifications()
    declarations_data = build_declarations()

    data = PDFData(
        header=header_data,
        applicant=applicant_data,
        coverage=coverage_data,
        payment=payment_data,
        broker=broker_data,
        property=property_data,
        risk_data=risk_data,
        plot_coordinates=coords_data,
        croqui_bytes=croqui_bytes,
        risk_questionnaire=risk_questionnaire_data,
        information_html_blocks=acceptance_data,
        grace_period_html=grace_period_data,
        coverage_restrictions_html=coverage_restrictions_data,
        available_documents_html=available_documents_data,
        excluded_risks_html=excluded_risks_data,
        propopent_notifications_html_block=notifications_data,
        declarations_and_commitments_html_block=declarations_data,
    )
    return data
