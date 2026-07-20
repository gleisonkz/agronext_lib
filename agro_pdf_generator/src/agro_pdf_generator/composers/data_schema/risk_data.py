import agronext_procurement as procurement
from agronext_procurement.views.common import CoverageFinancialsView, PropertyView

from ...utils import (
    format_decimal,
    format_dms_coordinates,
    format_monetary_value,
    polygon_centroid,
)


def _to_alpha_suffix(index: int) -> str:
    """Convert 1-based index to alphabetical suffix (1 -> a, 27 -> aa)."""
    if index < 1:
        return "a"

    letters: list[str] = []
    current = index
    while current > 0:
        current -= 1
        letters.append(chr(ord("a") + (current % 26)))
        current //= 26

    return "".join(reversed(letters))


def build_risk_data(
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
                for item_index, plot_item in enumerate(plot.items, start=1):
                    deductible_fraction = float(financials.deductible_details.percentage or 0)
                    if deductible_fraction > 1:
                        deductible_fraction /= 100
                    coverage_rate = float(financials.coverage_rate or 0)
                    if coverage_rate > 1:
                        coverage_rate /= 100
                    partial_deductible = (
                        deductible_fraction * plot_item.total_value
                    )
                    partial_premium = plot_item.total_value * coverage_rate
                    risk_data.append(
                        [
                            str(i).rjust(2, "0"),
                            plot.name,
                            f"{i}-{_to_alpha_suffix(item_index)}",
                            plot_item.crop_variety,
                            format_decimal(value=plot_item.yield_area_ha, precision=2),
                            format_decimal(value=plot_item.yield_ton_ha, precision=3),
                            format_monetary_value(plot_item.price_per_ton_brl),
                            format_monetary_value(plot_item.total_value),
                            format_monetary_value(partial_deductible),
                            format_monetary_value(partial_premium),
                        ]
                    )

    return risk_data


def build_policy_risk_items(
    view: procurement.ProposalView,
    financials: CoverageFinancialsView | None,
) -> list[list[str]]:
    if not view.properties:
        return []

    deductible = float(financials.deductible_details.percentage or 0) if financials else 0.0
    if deductible > 1:
        deductible /= 100
    coverage_rate = financials.coverage_rate if financials else 0.0
    if coverage_rate > 1:
        coverage_rate /= 100

    items: list[list[str]] = []
    item_index = 1

    for prop in view.properties:
        for crop_field in prop.crop_fields:
            for plot in crop_field.plots:
                latitude, longitude = polygon_centroid(plot.polygon.coordinates)
                coordinates = format_dms_coordinates(latitude, longitude)

                for item in plot.items:
                    lmg_value = item.total_value
                    premium = lmg_value * coverage_rate
                    deductible_value = lmg_value * deductible
                    pe_ton_ha = item.yield_ton_ha * (1 - deductible)

                    items.append(
                        [
                            str(item_index),
                            plot.name,
                            format_decimal(value=item.yield_area_ha),
                            format_decimal(value=item.price_per_ton_brl),
                            item.crop_variety,
                            format_decimal(
                                value=item.yield_ton_ha,
                                precision=4,
                            ),
                            format_monetary_value(lmg_value),
                            coordinates,
                            format_decimal(value=pe_ton_ha, precision=3),
                            format_monetary_value(lmg_value),
                            format_monetary_value(deductible_value),
                            format_monetary_value(premium),
                        ]
                    )
                    item_index += 1

    return items
