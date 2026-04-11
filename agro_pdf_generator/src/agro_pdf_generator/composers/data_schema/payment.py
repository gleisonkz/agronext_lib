import agronext_procurement_repositories as repositories
from agronext_procurement.views.common import CoverageFinancialsView

from ...schemas import BrokerData, CoverageData, PaymentData
from ...utils import format_monetary_value, next_month


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
    installments_date = metadata.installments_start_date

    if metadata.number_of_installments:
        broker_data.commission_pct = f"{financials.broker_comission_rate:.2f} %"

        payment_data.installments = [
            [
                installment.installment_number,
                installment.total_amount,
                installment.due_date,
            ]
            for installment in billing_info
        ]
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

        payment_data.installments = [
            [
                installment.installment_number,
                installment.total_amount,
                installment.due_date,
            ]
            for installment in billing_info
        ]

    return payment_data
