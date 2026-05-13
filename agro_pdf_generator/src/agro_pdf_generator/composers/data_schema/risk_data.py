from agronext_procurement.views.common import CoverageFinancialsView, PropertyView

from ...utils import format_monetary_value


_SEPARATOR_TRANSLATION = str.maketrans({",": ".", ".": ","})


def _format_number(value: float, precision: int) -> str:
    #TODO: review if it can be replaced by format_decimal util function, or, increment the format decimal to have the separator translation
    formatted = f"{value:.{precision}f}"
    return formatted.translate(_SEPARATOR_TRANSLATION)


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
                    partial_deductible = (
                        financials.deductible_details.percentage * plot_item.total_value
                    )
                    partial_premium = plot_item.total_value * financials.coverage_rate
                    risk_data.append(
                        [
                            str(i).rjust(2, "0"),
                            plot.name,
                            f"{i}-{_to_alpha_suffix(item_index)}",
                            plot_item.crop_variety,
                            _format_number(plot_item.yield_area_ha, precision=2),
                            _format_number(plot_item.yield_ton_ha, precision=3),
                            format_monetary_value(plot_item.price_per_ton_brl),
                            format_monetary_value(plot_item.total_value),
                            format_monetary_value(partial_deductible),
                            format_monetary_value(partial_premium),
                        ]
                    )

    return risk_data
