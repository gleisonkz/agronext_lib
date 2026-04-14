import agronext_procurement_repositories as repositories
from agronext_procurement.views.common import CoverageFinancialsView

from ...schemas import BrokerData, CoverageData, PaymentData


def _build_installment_rows(billing_info: list | None) -> list[list[str]]:
    if not billing_info:
        return []

    rows: list[list[str]] = []
    for installment in billing_info:
        rows.append(
            [
                str(installment.installment_number),
                installment.total_amount,
                str(installment.due_date),
            ]
        )

    return rows


def _parse_brl_amount(value: str | None) -> float:
    if not value:
        return 0.0

    normalized = "".join(ch for ch in value if ch.isdigit() or ch in ",.-")
    if not normalized:
        return 0.0

    if "," in normalized and "." in normalized:
        normalized = normalized.replace(".", "").replace(",", ".")
    elif "," in normalized:
        normalized = normalized.replace(",", ".")

    try:
        return float(normalized)
    except ValueError:
        return 0.0


def _apply_subsidy_installment_rule(
    installments: list[list[str]],
    coverage_data: CoverageData,
) -> list[list[str]]:
    filtered_installments = installments

    state_subsidy = _parse_brl_amount(coverage_data.state_subsidy_brl)
    federal_subsidy = _parse_brl_amount(coverage_data.federal_subsidy_brl)

    if state_subsidy > 0:
        filtered_installments = filtered_installments[:-1]

    if federal_subsidy > 0:
        filtered_installments = filtered_installments[:-1]

    return filtered_installments


def build_quotation_payment(
    metadata: repositories.QuotationMetadata,
    financials: CoverageFinancialsView,
    broker_data: BrokerData,
    coverage_data: CoverageData,
    billing_info: list | None = None,
) -> PaymentData:
    # Payment
    payment_data = PaymentData(
        payment_method="",
        number_of_installments="",
        net_premium="",
        policy_cost="R$ 0,00",
        iof="Isento",
        total_premium="",
        installments=[],
    )

    payment_data.payment_method = metadata.payment_condition
    payment_data.number_of_installments = str(metadata.number_of_installments)
    payment_data.net_premium = coverage_data.net_premium
    payment_data.total_premium = coverage_data.applicant_value

    if metadata.number_of_installments:
        broker_data.commission_pct = f"{financials.broker_comission_rate:.2f} %"
        payment_data.installments = _apply_subsidy_installment_rule(
            _build_installment_rows(billing_info),
            coverage_data,
        )
    return payment_data


def build_proposal_payment(
    metadata: repositories.QuotationMetadata,
    financials: CoverageFinancialsView,
    broker_data: BrokerData,
    coverage_data: CoverageData,
    billing_info: list | None = None,
) -> PaymentData:
    # Payment
    payment_data = PaymentData(
        payment_method="",
        number_of_installments="",
        net_premium="",
        policy_cost="R$ 0,00",
        iof="Isento",
        total_premium="",
        installments=[],
    )

    payment_data.payment_method = metadata.payment_condition
    payment_data.number_of_installments = str(metadata.number_of_installments)
    payment_data.net_premium = coverage_data.net_premium
    payment_data.total_premium = coverage_data.applicant_value

    if metadata.number_of_installments:
        broker_data.commission_pct = f"{financials.broker_comission_rate:.2f} %"
        payment_data.installments = _apply_subsidy_installment_rule(
            _build_installment_rows(billing_info),
            coverage_data,
        )

    return payment_data
