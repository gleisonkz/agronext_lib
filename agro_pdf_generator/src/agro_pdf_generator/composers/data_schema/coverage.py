import agronext_procurement as procurement
from agronext_procurement.views.common import CoverageDetailsView

from ...schemas import CoverageData
from ...utils import format_monetary_value


def build_quotation_coverage(view: procurement.QuotationView, coverage: CoverageDetailsView):

    # Coverage
    coverage_data = CoverageData(
        name="101 - Granizo (Pêra)",
        policy_limit_brl="",
        deductible_pct="",
        coverage_rate_pct="",
        tariff_premium="",
        net_premium="",
        federal_subsidy_brl="",
        state_subsidy_brl="",
        applicant_value="",
        # Info in the property
        insured_area_ha="",
        plot_count="",
    )
    if coverage and coverage.financials:
        coverage_data.policy_limit_brl = format_monetary_value(coverage.financials.policy_limit)
        coverage_data.deductible_pct = f"{coverage.financials.deductible_details.percentage:.2f}%"

        coverate_rate_pct = coverage.financials.coverage_rate * 100 / coverage.financials.gross_premium
        coverage_data.coverage_rate_pct = f"{coverate_rate_pct:.2f}%"

        coverage_data.tariff_premium = format_monetary_value(coverage.financials.broker_comission_rate)
        coverage_data.net_premium = format_monetary_value(coverage.financials.net_estimated_premium)
        coverage_data.federal_subsidy_brl = format_monetary_value(coverage.financials.federal_subsidy.max_amount_brl)
        coverage_data.state_subsidy_brl = format_monetary_value(coverage.financials.state_subsidy.max_amount_brl)
        coverage_data.applicant_value = format_monetary_value(coverage.financials.gross_premium)


    for prop in (view.properties or []):
        total_plots, total_area = 0, 0.0
        for crop_fields in prop.crop_fields:
            total_area += crop_fields.area_ha
            total_plots += len(crop_fields.plots)

        coverage_data.insured_area_ha = f"{total_area:.2f}"
        coverage_data.plot_count = str(total_plots)

    return coverage_data
