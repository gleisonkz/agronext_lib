from agronext_procurement.views.common import PropertyView, CoordinatesView


def build_coordinates(properties: list[PropertyView]) -> list[list[str]]:
    coordinates_data: list[list[str]] = []
    if not properties:
        return coordinates_data

    for prop in properties:
        for crop_fields in prop.crop_fields:
            for i, plot in enumerate(crop_fields.plots, start=1):
                coords = [CoordinatesView(latitude=latitude, longitude=longitude) for (latitude, longitude) in plot.polygon.coordinates]
                centroid = plot.polygon._source._calculate_centroid(coords)
                coordinates_data.append([str(i), f"({centroid.latitude:.6f}, {centroid.longitude:.6f})"])

    return coordinates_data
