import agronext_procurement as procurement
import agronext_procurement_repositories as repositories

from agro_pdf_generator.composers.data_schema.prop_declaration import (
    build_proposal_proponent_declaration,
)

from ...schemas import PDFData
from .acceptance import build_acceptance
from .address import build_proposal_address
from .applicant import build_applicant
from .authorization import (
    build_proposal_authorization_term,
    build_proposal_beneficiary_authorization,
)
from .authorized import build_proposal_authorized_persons
from .available_documents import build_available_documents
from .beneficiaries import build_proposal_beneficiaries
from .broker import build_proposal_broker, build_quotation_broker
from .coordinates import build_coordinates
from .coverage import build_proposal_coverage, build_quotation_coverage
from .coverage_restrictions import build_coverage_restrictions
from .declarations import build_declarations
from .excluded_risks import build_excluded_risks
from .grace_period import build_grace_period
from .header import build_header
from .land_property import build_proposal_property, build_quotation_property
from .lgpd import build_lgpd_consent
from .notifications import build_proponent_notifications
from .payment import build_proposal_payment, build_quotation_payment
from .political_exposure import build_proposal_political_exposure
from .risk_data import build_risk_data
from .risk_questionnaire import build_risk_questionnaire
from .subsidy import (
    build_proposal_federal_subsidy_term,
    build_proposal_state_authorization_term,
    build_proposal_state_subsidy_term,
    build_proposal_subsidy_questions,
)


def build_quotation_data_from_domain(
    view: procurement.QuotationView,
    metadata: repositories.QuotationMetadata,
    broker_details: dict,
    croqui_bytes: bytes,
) -> PDFData:
    coverage = view.coverages[0].coverage if view.coverages else None
    financials = coverage.financials if coverage else None

    header_data = build_header(
        view, metadata, coverage, proposal_number=None, policy_id=None
    )
    applicant_data = build_applicant(view)

    coverage_data = build_quotation_coverage(view, coverage)
    broker_data = build_quotation_broker(broker_details)
    payment_data = build_quotation_payment(
        metadata=metadata,
        financials=financials,
        coverage_data=coverage_data,
    )

    # Removed stale TODO markers
    property_data = build_quotation_property(view)
    risk_data = build_risk_data(view.properties, financials)
    coords_data = build_coordinates(view.properties)
    risk_questionnaire_data = build_risk_questionnaire(metadata)
    acceptance_data = build_acceptance()
    grace_period_data = build_grace_period()
    coverage_restrictions_data = build_coverage_restrictions()
    available_documents_data = build_available_documents(["Cobertura 101 - Granizo (Pêra)"])
    excluded_risks_data = build_excluded_risks()
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


def build_proposal_data_from_domain(
    view: procurement.ProposalView,
    quotation_metadata: repositories.QuotationMetadata,
    metadata: repositories.ProposalMetadata,
    broker_details: dict,
    croqui_bytes: bytes,
) -> PDFData:
    coverage = view.coverages[0].coverage if view.coverages else None
    financials = coverage.financials if coverage else None

    header_data = build_header(
        view,
        quotation_metadata,
        coverage,
        proposal_number=metadata.public_id,
        policy_id=metadata.policy_id,
    )
    applicant_data = build_applicant(view)

    address_data = build_proposal_address(view)

    political_exposure = build_proposal_political_exposure(
        applicant_data, quotation_metadata.has_political_exposure
    )

    coverage_data = build_proposal_coverage(view, coverage)
    broker_data = build_proposal_broker(broker_details)
    payment_data = build_proposal_payment(
        metadata=quotation_metadata,
        financials=financials,
        broker_data=broker_data,
        coverage_data=coverage_data,
    )

    property_data = build_proposal_property(view)
    risk_data = build_risk_data(view.properties, financials)
    coords_data = build_coordinates(view.properties)
    risk_questionnaire_data = build_risk_questionnaire(quotation_metadata)

    beneficiaries_data = build_proposal_beneficiaries(view.beneficiaries)
    authorized_data = build_proposal_authorized_persons(
        quotation_metadata.authorized_for_inspection
    )

    acceptance_data = build_acceptance()
    grace_period_data = build_grace_period()
    coverage_restrictions_data = build_coverage_restrictions()
    available_documents_data = build_available_documents(["Cobertura 101 - Granizo (Pêra)"])
    excluded_risks_data = build_excluded_risks()

    authorization_data = build_proposal_authorization_term(
        view=view,
        proposal_number=str(metadata.public_id)
        if metadata.public_id is not None
        else "",
    )
    authorization_beneficiary_data = build_proposal_beneficiary_authorization(
        view.beneficiaries
    )

    lgpd_data = build_lgpd_consent(applicant_data)

    proponent_declaration_data = build_proposal_proponent_declaration()

    federal_subsidy_term_data = build_proposal_federal_subsidy_term(quotation_metadata)

    subsidy_data = build_proposal_subsidy_questions(quotation_metadata)
    state_subsidy_term_data = build_proposal_state_subsidy_term(quotation_metadata)
    state_authorization_term_data = build_proposal_state_authorization_term(
        quotation_metadata
    )

    data = PDFData(
        header=header_data,
        residential_address=address_data,
        authorization_term=authorization_data,
        authorization_beneficiary=authorization_beneficiary_data,
        political_exposure=political_exposure,
        subsidy=subsidy_data,
        applicant=applicant_data,
        coverage=coverage_data,
        payment=payment_data,
        broker=broker_data,
        property=property_data,
        beneficiaries=beneficiaries_data,
        has_authorized_persons="Sim" if authorized_data else "Não",
        lgpd_consent=lgpd_data,
        risk_data=risk_data,
        plot_coordinates=coords_data,
        croqui_bytes=croqui_bytes,
        federal_subsidy_term=federal_subsidy_term_data,
        risk_questionnaire=risk_questionnaire_data,
        authorized_persons=authorized_data,
        information_html_blocks=acceptance_data,
        grace_period_html=grace_period_data,
        coverage_restrictions_html=coverage_restrictions_data,
        available_documents_html=available_documents_data,
        proponent_declaration=proponent_declaration_data,
        excluded_risks_html=excluded_risks_data,
        observations=quotation_metadata.observation or "",
        state_authorization_term=state_authorization_term_data,
        state_subsidy_term=state_subsidy_term_data,
    )
    return data
