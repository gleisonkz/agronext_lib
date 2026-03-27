import agronext_procurement_repositories as repositories
from agronext_procurement.views.common import CoverageFinancialsView

from ...schemas import BrokerData, CoverageData, PaymentData
from ...utils import format_monetary_value, next_month


def build_quotation_payment(
    metadata: repositories.QuotationMetadata,
    financials: CoverageFinancialsView,
    broker_data: BrokerData,
    coverage_data: CoverageData,
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
        total_cents = int(round(financials.gross_premium * 100))

        base = total_cents // metadata.number_of_installments
        remainder = total_cents - (base * metadata.number_of_installments)
        first = (base + remainder) / 100
        others = base / 100

        payment_values = [first] + [others] * (metadata.number_of_installments - 1)

        for i, installment_amount in enumerate(payment_values):
            payment_data.installments.append(
                [
                    f"Parcela {i + 1}",
                    format_monetary_value(installment_amount),
                    installments_date.strftime("%d/%m/%Y"),
                ]
            )
            installments_date = next_month(installments_date)

    return payment_data


def build_proposal_payment(
    metadata: repositories.QuotationMetadata,
    financials: CoverageFinancialsView,
    broker_data: BrokerData,
    coverage_data: CoverageData,
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
        total_cents = int(round(financials.gross_premium * 100))

        base = total_cents // metadata.number_of_installments
        remainder = total_cents - (base * metadata.number_of_installments)
        first = (base + remainder) / 100
        others = base / 100

        payment_values = [first] + [others] * (metadata.number_of_installments - 1)

        for i, installment_amount in enumerate(payment_values):
            payment_data.installments.append(
                [
                    f"Parcela {i + 1}",
                    format_monetary_value(installment_amount),
                    installments_date.strftime("%d/%m/%Y"),
                ]
            )
            installments_date = next_month(installments_date)

    return payment_data