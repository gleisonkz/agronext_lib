import agronext_procurement as procurement
import agronext_procurement_repositories as repositories
from agronext_procurement.views.common import CoverageDetailsView
import unicodedata

from ...schemas import CoverageData
from ...utils import format_monetary_value


def _normalize_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch)).casefold()


def _extract_coverage_name_from_documents(docs: list | None) -> str:
    if not docs:
        return ""

    crops = list(repositories.CROP_TAXONOMY_DICT.values())
    perils = list(repositories.PERIL_TAXONOMY_DICT.values())

    normalized_crops = {crop: _normalize_text(crop) for crop in crops}
    normalized_perils = {peril: _normalize_text(peril) for peril in perils}

    for doc in docs:
        doc_name = (getattr(doc, "name", None) or "").strip()
        if not doc_name:
            continue

        normalized_name = _normalize_text(doc_name)

        matched_crop = next(
            (crop for crop, crop_norm in normalized_crops.items() if crop_norm in normalized_name),
            None,
        )
        matched_peril = next(
            (peril for peril, peril_norm in normalized_perils.items() if peril_norm in normalized_name),
            None,
        )

        if matched_crop and matched_peril:
            return f"{matched_crop} - {matched_peril}"

    return ""


def build_coverage(
    view: procurement.ProposalView | procurement.QuotationView,
    coverage: CoverageDetailsView,
    quotation_metadata: repositories.QuotationMetadata | None = None,
):
    
    # Coverage
    coverage_name = _extract_coverage_name_from_documents(
        quotation_metadata.documents if quotation_metadata else None
    )

    if not coverage_name and coverage:
        peril = repositories.PERIL_TAXONOMY_DICT.get(
            coverage.conditions.main_peril,
            coverage.conditions.main_peril,
        )
        crop = repositories.CROP_TAXONOMY_DICT.get(
            coverage.conditions.crop.crop,
            coverage.conditions.crop.crop,
        )
        coverage_name = f"{crop} - {peril}"

    coverage_data = CoverageData(
        name=coverage_name,
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

        coverate_rate_pct = coverage.financials.coverage_rate
        coverage_data.coverage_rate_pct = f"{coverate_rate_pct:.2f}%"

        net_premium = coverage.financials.net_estimated_premium
        federal_subsidy = coverage.financials.federal_subsidy_discount
        state_subsidy = coverage.financials.state_subsidy_discount
        applicant_approx_value = max(net_premium - federal_subsidy - state_subsidy, 0)

        coverage_data.tariff_premium = format_monetary_value(net_premium)
        coverage_data.net_premium = format_monetary_value(net_premium)
        coverage_data.federal_subsidy_brl = format_monetary_value(federal_subsidy)
        coverage_data.state_subsidy_brl = format_monetary_value(state_subsidy)
        coverage_data.applicant_value = format_monetary_value(applicant_approx_value)


    for prop in (view.properties or []):
        total_plots, total_area = 0, 0.0
        for crop_fields in prop.crop_fields:
            total_area += crop_fields.area_ha
            total_plots += len(crop_fields.plots)

        coverage_data.insured_area_ha = f"{total_area:.2f}"
        coverage_data.plot_count = str(total_plots)

    return coverage_data