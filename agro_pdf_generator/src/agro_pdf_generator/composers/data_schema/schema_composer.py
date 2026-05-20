from datetime import datetime

import agronext_procurement as procurement
import agronext_procurement_repositories as repositories

from ...schemas import PDFData
from .acceptance import build_acceptance, build_simulation_general_info_html
from .address import build_proposal_address
from .applicant import build_applicant, build_simulation_applicant
from .authorization import (
    build_proposal_authorization_term,
    build_proposal_beneficiary_authorization,
)
from .authorized import build_proposal_authorized_persons
from .available_documents import build_available_documents
from .beneficiaries import build_proposal_beneficiaries
from .broker import build_broker
from .coordinates import build_coordinates
from .coverage import build_coverage, build_simulation_coverage
from .coverage_restrictions import build_coverage_restrictions
from .declarations import build_declarations
from .excluded_risks import build_excluded_risks
from .grace_period import build_grace_period
from .header import build_header, build_simulation_header
from .land_property import build_property, build_simulation_property
from .lgpd import build_lgpd_consent
from .notifications import build_proponent_notifications
from .payment import build_payment
from .political_exposure import build_proposal_political_exposure
from .prop_declaration import build_proposal_proponent_declaration
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
    proposal_metadata: repositories.ProposalMetadata | None,
    broker_details: dict,
    croqui_bytes: bytes,
    municipality_code: str | None = None,
    billing_info: list | None = None,
    header_logo_path: str | None = None,
) -> PDFData:
    coverage = view.coverages[0].coverage if view.coverages else None
    financials = coverage.financials if coverage else None

    proposal_number = (
        proposal_metadata.proposal_id
        if proposal_metadata and proposal_metadata.proposal_id is not None
        else metadata.proposal_id
    )

    header_data = build_header(
        view,
        metadata,
        coverage,
        proposal_number=proposal_number,
        policy_id=proposal_metadata.policy_id if proposal_metadata else None,
        logo_path=header_logo_path,
    )
    applicant_data = build_applicant(view)

    coverage_data = build_coverage(view, coverage, metadata)
    broker_data = build_broker(broker_details)
    payment_data = build_payment(
        metadata=metadata,
        financials=financials,
        broker_data=broker_data,
        coverage_data=coverage_data,
        billing_info=billing_info,
    )

    property_data = build_property(view, municipality_code=municipality_code)
    risk_data = build_risk_data(view.properties, financials)
    coords_data = build_coordinates(view.properties)
    risk_questionnaire_data = build_risk_questionnaire(metadata)
    acceptance_data = build_acceptance()
    grace_period_data = build_grace_period()
    coverage_restrictions_data = build_coverage_restrictions()
    available_documents_data = build_available_documents(metadata.documents)
    excluded_risks_data = build_excluded_risks()
    notifications_data = build_proponent_notifications(is_quotation=True)
    declarations_data = build_declarations(is_quotation=True)

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
    municipality_code: str | None = None,
    billing_info: list | None = None,
    header_logo_path: str | None = None,
    federal_subsidy_logo_path: str | None = None,
    state_subsidy_logo_path: str | None = None,
) -> PDFData:
    coverage = view.coverages[0].coverage if view.coverages else None
    financials = coverage.financials if coverage else None

    header_data = build_header(
        view,
        quotation_metadata,
        coverage,
        proposal_number=metadata.proposal_id,
        policy_id=metadata.policy_id,
        logo_path=header_logo_path,
    )
    applicant_data = build_applicant(view)

    address_data = build_proposal_address(view)

    political_exposure = build_proposal_political_exposure(
        applicant_data, quotation_metadata.has_political_exposure
    )

    coverage_data = build_coverage(view, coverage, quotation_metadata)
    broker_data = build_broker(broker_details)
    payment_data = build_payment(
        metadata=quotation_metadata,
        financials=financials,
        broker_data=broker_data,
        coverage_data=coverage_data,
        billing_info=billing_info,
    )

    property_data = build_property(view, municipality_code=municipality_code)
    risk_data = build_risk_data(view.properties, financials)
    coords_data = build_coordinates(view.properties)
    risk_questionnaire_data = build_risk_questionnaire(quotation_metadata)

    beneficiaries_data = build_proposal_beneficiaries(view.beneficiaries)
    authorized_data = build_proposal_authorized_persons(
        quotation_metadata.authorized_for_inspection
    )

    acceptance_data = build_acceptance()
    notifications_data = build_proponent_notifications(is_quotation=False)
    grace_period_data = build_grace_period()
    coverage_restrictions_data = build_coverage_restrictions()
    available_documents_data = build_available_documents(quotation_metadata.documents)
    excluded_risks_data = build_excluded_risks()
    declarations_data = build_declarations(is_quotation=False)

    authorization_data = build_proposal_authorization_term(
        view=view,
        proposal_number=str(metadata.proposal_id)
        if metadata.proposal_id is not None
        else "",
    )
    authorization_beneficiary_data = build_proposal_beneficiary_authorization(
        view.beneficiaries
    )

    lgpd_data = build_lgpd_consent(applicant_data)

    proponent_declaration_data = build_proposal_proponent_declaration()

    federal_subsidy_term_data = build_proposal_federal_subsidy_term(
        quotation_metadata,
        federal_logo_path=federal_subsidy_logo_path,
    )

    subsidy_data = build_proposal_subsidy_questions(quotation_metadata)
    state_subsidy_term_data = build_proposal_state_subsidy_term(
        quotation_metadata,
        state_logo_path=state_subsidy_logo_path,
    )
    state_authorization_term_data = build_proposal_state_authorization_term(
        quotation_metadata,
        state_logo_path=state_subsidy_logo_path,
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
        propopent_notifications_html_block=notifications_data,
        grace_period_html=grace_period_data,
        coverage_restrictions_html=coverage_restrictions_data,
        available_documents_html=available_documents_data,
        proponent_declaration=proponent_declaration_data,
        excluded_risks_html=excluded_risks_data,
        declarations_and_commitments_html_block=declarations_data,
        observations=quotation_metadata.observation or "Não informado",
        state_authorization_term=state_authorization_term_data,
        state_subsidy_term=state_subsidy_term_data,
    )
    return data

def build_simulation_pdf_data(
    *,
    simulation_date: datetime,
    harvest: int,
    coverage_id: int,
    crop: str,
    peril: str,
    proponent_name: str,
    proponent_phone: str,
    state: str,
    city: str,
    country: str | None,
    latitude: float,
    longitude: float,
    deductible_percentage: float,
    area_ha: float,
    productivity_ton_ha: float,
    price_per_ton: float,
    policy_limit: float,
    premium: float,
    rate: float,
    federal_subsidy_percentage: float,
    federal_subsidy_discount: float,
    state_subsidy_percentage: float,
    state_subsidy_discount: float,
    value_with_only_federal_subsidy: float,
    value_with_only_state_subsidy: float,
    discounted_premium: float,
    broker_details: dict,
    header_logo_path: str | None = None,
    general_info_text: str | None = None,
) -> PDFData:
    header_data = build_simulation_header(
        simulation_date=simulation_date,
        harvest=harvest,
        coverage_id=coverage_id,
        crop=crop,
        peril=peril,
        header_logo_path=header_logo_path,
    )

    applicant_data = build_simulation_applicant(
        name=proponent_name,
        phone=proponent_phone,
    )

    location_data = build_simulation_property(
        state=state,
        city=city,
        country=country,
        latitude=latitude,
        longitude=longitude,
    )

    productivity_data = build_simulation_coverage(
        deductible_percentage=deductible_percentage,
        area_ha=area_ha,
        productivity_ton_ha=productivity_ton_ha,
        price_per_ton=price_per_ton,
        policy_limit=policy_limit,
        premium=premium,
        rate=rate,
        federal_subsidy_percentage=federal_subsidy_percentage,
        federal_subsidy_discount=federal_subsidy_discount,
        state_subsidy_percentage=state_subsidy_percentage,
        state_subsidy_discount=state_subsidy_discount,
        value_with_only_federal_subsidy=value_with_only_federal_subsidy,
        value_with_only_state_subsidy=value_with_only_state_subsidy,
        discounted_premium=discounted_premium,
    )

    broker_data = build_broker(broker_details)

    information_blocks = [
        build_simulation_general_info_html(general_info_text),
    ]

    return PDFData(
        header=header_data,
        applicant=applicant_data,
        property=location_data,
        coverage=productivity_data,
        broker=broker_data,
        information_html_blocks=information_blocks,
    )
