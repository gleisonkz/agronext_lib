from __future__ import annotations

import agronext_procurement as procurement
import agronext_procurement_repositories as repositories

from ...schemas import PolicyDocumentData
from ...utils import format_decimal
from .applicant import build_policy_insured
from .beneficiaries import build_policy_beneficiaries
from .broker import build_policy_broker_from_user
from .coverage import build_policy_coverage_details, build_policy_coverage_lines
from .header import build_policy_issue_date
from .land_property import build_policy_property
from .payment import build_policy_installment_lines
from .risk_data import build_policy_risk_items


def build_policy_data_from_domain(
    view: procurement.ProposalView,
    quotation_metadata: repositories.QuotationMetadata,
    proposal_metadata: repositories.ProposalMetadata,
    broker_user: repositories.tables.BrokerUser,
    municipality_code: str | None = None,
    broker_user_details: dict | None = None,
    billing_info: list | None = None,
) -> PolicyDocumentData:
    coverage = view.coverages[0].coverage if view.coverages else None
    financials = coverage.financials if coverage else None
    insured_data = build_policy_insured(view)
    property_data = build_policy_property(view, municipality_code=municipality_code)
    beneficiaries_data = build_policy_beneficiaries(view.beneficiaries)
    primary_beneficiary = beneficiaries_data[0] if beneficiaries_data else None
    broker_data = build_policy_broker_from_user(
        broker_user,
        broker_user_details=broker_user_details,
    )
    coverage_data = build_policy_coverage_details(coverage)
    coverage_lines = build_policy_coverage_lines(coverage)
    installments = build_policy_installment_lines(
        quotation_metadata,
        financials,
        billing_info=billing_info,
    )
    risk_items = build_policy_risk_items(view, financials)
    issue_date = build_policy_issue_date(proposal_metadata)

    proposal_number = proposal_metadata.proposal_id or proposal_metadata.public_id or view.id
    policy_number = proposal_metadata.policy_id or "Não informado"
    insured_items_count = len(risk_items) or view.items_count or 0

    return PolicyDocumentData(
        proposal_number=str(proposal_number),
        issue_date=issue_date,
        harvest=_build_harvest_label(quotation_metadata.harvest),
        product=coverage_data["product"],
        policy_number=str(policy_number),
        endorsement_number="0",
        branch="01 - Rio de Janeiro",
        susep_process="15414.004511/2012-58",
        main_coverage=coverage_data["main_coverage"],
        validity_period=coverage_data["validity_period"],
        insured_name=insured_data["name"],
        insured_social_name=insured_data["social_name"],
        insured_document=insured_data["document"],
        insured_birth_date=insured_data["birth_date"],
        insured_additional_document=insured_data["additional_document"],
        insured_document_issuing_authority=insured_data["document_issuing_authority"],
        insured_document_issue_date=insured_data["document_issue_date"],
        insured_email=insured_data["email"],
        insured_address=insured_data["address"],
        insured_neighborhood=insured_data["neighborhood"],
        insured_zip_code=insured_data["zip_code"],
        insured_city_state=insured_data["city_state"],
        insured_phone=insured_data["phone"],
        property_address=property_data["address"],
        property_neighborhood=property_data["neighborhood"],
        property_zip_code=property_data["zip_code"],
        property_city_state=property_data["city_state"],
        property_bacen_code=property_data["bacen_code"],
        property_name=property_data["name"],
        property_coordinates=property_data["coordinates"],
        beneficiary_name=primary_beneficiary.name if primary_beneficiary else "Não informado",
        beneficiary_document=primary_beneficiary.cpf if primary_beneficiary else "Não informado",
        beneficiary_share=primary_beneficiary.percentage if primary_beneficiary else "0,00%",
        broker_name=broker_data["name"],
        broker_document=broker_data["document"],
        broker_susep_code=broker_data["susep_code"],
        broker_address=broker_data["address"],
        broker_neighborhood=broker_data["neighborhood"],
        broker_zip_code=broker_data["zip_code"],
        broker_city_state=broker_data["city_state"],
        broker_phone=broker_data["phone"],
        crop=coverage_data["crop"],
        total_area=format_decimal(value=view.total_insured_area_ha or 0.0),
        lmga=coverage_data["lmga"],
        bacen_code="11283005",
        insured_items=str(insured_items_count),
        total_premium=coverage_data["total_premium"],
        beneficiaries=beneficiaries_data,
        coverage_lines=coverage_lines,
        policy_net_premium=coverage_data["policy_net_premium"],
        policy_cost="R$ 0,00",
        iof="R$ 0,00",
        premium_to_pay=coverage_data["premium_to_pay"],
        installments=installments,
        risk_items=risk_items,
        has_beneficiary=bool(view.beneficiaries),
    )


def _build_harvest_label(harvest: object) -> str:
    value = str(harvest).strip() if harvest is not None else ""
    if not value:
        return "Não informado"

    try:
        year = int(value)
    except ValueError:
        return value

    return f"{year}/{year + 1}"
