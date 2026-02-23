from agronext_procurement.views.common import CoverageFinancialsView, PropertyView


def build_quotation_risk_data(
    properties: list[PropertyView],
    financials: CoverageFinancialsView,
) -> list[list[str]]:
    # Risk
    risk_data = []
    if not properties:
        return risk_data

    for prop in properties:
        for crop_fields in prop.crop_fields:
            for i, plot in enumerate(crop_fields.plots, start=1):
                for plot_item in plot.items:
                    partial_deductible = financials.deductible_details.percentage * plot_item.total_value
                    partial_premium = plot_item.total_value * financials.coverage_rate
                    risk_data.append(
                        [
                            str(i),
                            plot.name,
                            plot_item.name,
                            plot_item.crop_variety,
                            f"{plot_item.yield_area_ha:.2f}",
                            f"{plot_item.yield_ton_ha:.2f}",
                            f"{plot_item.yield_output_tons:.2f}",
                            f"{plot_item.total_value:,.2f}",
                            f"{partial_deductible:,.2f}",
                            f"{partial_premium:,.2f}",
                        ]
                    )

    return risk_data
