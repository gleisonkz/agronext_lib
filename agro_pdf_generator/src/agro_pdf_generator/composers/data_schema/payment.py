from datetime import datetime

import agronext_procurement_repositories as repositories
from agronext_procurement.views.common import CoverageFinancialsView

from ...schemas import BrokerData, CoverageData, PaymentData
from ...utils import format_monetary_value, parse_brl_amount


def _build_installment_rows(billing_info: list | None) -> list[list[str]]:
    if not billing_info:
        return []

    rows: list[list[str]] = []
    for installment in billing_info:
        rows.append(
            [
                str(installment.installment_number).rjust(2, "0"),
                installment.total_amount,
                datetime.strptime(installment.due_date, "%Y-%m-%d").strftime("%d/%m/%Y"),
            ]
        )

    return rows


def _apply_subsidy_installment_rule(
    installments: list[list[str]],
    coverage_data: CoverageData,
) -> list[list[str]]:
    filtered_installments = installments

    state_subsidy = parse_brl_amount(coverage_data.state_subsidy_brl)
    federal_subsidy = parse_brl_amount(coverage_data.federal_subsidy_brl)

    if state_subsidy > 0:
        filtered_installments = filtered_installments[:-1]

    if federal_subsidy > 0:
        filtered_installments = filtered_installments[:-1]

    return filtered_installments

def _resolve_policy_installment_payer(
    installment_number: int,
    number_of_installments: int,
    has_state_subsidy: bool,
    has_federal_subsidy: bool,
) -> str:
    if installment_number <= number_of_installments:
        return "Segurado"

    first_subsidy_number = number_of_installments + 1
    if has_state_subsidy and installment_number == first_subsidy_number:
        return "Subvenção Estadual"

    if has_federal_subsidy:
        federal_number = first_subsidy_number + 1 if has_state_subsidy else first_subsidy_number
        if installment_number == federal_number:
            return "Subvenção Federal"

    return "Segurado"


def build_payment(
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


def build_policy_installment_lines(
    metadata: repositories.QuotationMetadata,
    financials: CoverageFinancialsView | None,
    billing_info: list | None = None,
) -> list[list[str]]:
    if not financials or not billing_info:
        return []

    number_of_installments = metadata.number_of_installments or 1
    has_state_subsidy = financials.state_subsidy_discount > 0
    has_federal_subsidy = financials.federal_subsidy_discount > 0

    lines: list[list[str]] = []
    for installment in billing_info:
        number = getattr(installment, "installment_number", None)
        title = getattr(installment, "title", None)
        due_date = getattr(installment, "due_date", None)
        total_amount = getattr(installment, "total_amount", None)

        if isinstance(installment, dict):
            number = installment.get("installment_number", installment.get("nr_parcela", number))
            title = installment.get("title", installment.get("titulo", title))
            due_date = installment.get("due_date", installment.get("dt_vencimento", due_date))
            total_amount = installment.get("total_amount", installment.get("vl_total", total_amount))

        if number is None:
            continue

        try:
            installment_number = int(number)
        except (TypeError, ValueError):
            continue

        lines.append(
            [
                str(installment_number),
                datetime.strptime(due_date, "%Y-%m-%d").strftime("%d/%m/%Y") if due_date else "-",
                format_monetary_value(parse_brl_amount(total_amount)),
                str(title).strip() if title else "-",
                _resolve_policy_installment_payer(
                    installment_number=installment_number,
                    number_of_installments=number_of_installments,
                    has_state_subsidy=has_state_subsidy,
                    has_federal_subsidy=has_federal_subsidy,
                ),
            ]
        )

    return lines
