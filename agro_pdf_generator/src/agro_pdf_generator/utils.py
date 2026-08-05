from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import agronext_procurement as procurement
from agronext_procurement.views.common import PhoneView


def format_monetary_value(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def parse_brl_amount(value: str | None) -> float:
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


def next_month(date: datetime) -> datetime:
    month = date.month + 1 if date.month < 12 else 1
    year = date.year if date.month < 12 else date.year + 1
    try:
        new_date = date.replace(year=year, month=month)
    except ValueError:
        # If the day doesn't exist in the new month, set it to the last day of that month
        new_date = date.replace(year=year, month=month + 1, day=1) - timedelta(days=1)
    return new_date


def none_if_not_informed(value: object | None) -> object | None:
    text = str(value).strip() if value is not None else ""
    if not text or text.lower() == "não informado":
        return None
    return value


def format_phone(*, phone: PhoneView | str) -> str:
    if isinstance(phone, PhoneView):
        formatted_phone = format_phone_object(phone=phone)
        return formatted_phone if formatted_phone else ""
    elif isinstance(phone, str):
        formatted_phone = format_phone_number(phone=phone)
        return formatted_phone if formatted_phone else ""


def format_phone_number(*, phone: str) -> str:
    if not phone:
        return ""

    digits = "".join(char for char in phone if char.isdigit())

    if digits.startswith("55") and len(digits) in {12, 13}:
        digits = digits[2:]

    if len(digits) == 11:
        return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"

    if len(digits) == 10:
        return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
    
    if len(digits) == 9:
        return f"{digits[:5]}-{digits[5:]}"

    if len(digits) == 8:
        return f"{digits[:4]}-{digits[4:]}"

    return phone


def format_phone_object(*, phone: PhoneView) -> str:
    if not phone or not phone.number: 
        return ""

    area_code = getattr(phone, "area_code", None)
    number = getattr(phone, "number", None)

    formatted_number = ""
    if number is not None:
        formatted_number = format_phone_number(phone=str(number))
    if area_code is not None and number is not None:
        return f"({area_code}) {formatted_number}"
    if number is not None:
        return formatted_number
    return str(phone)


def format_decimal(*, value: float, precision: int = 2) -> str:
    return f"{value:.{precision}f}".replace(".", ",")


def format_percentage(*, value: float) -> str:
    return f"{value:.2f}%".replace(".", ",")


def format_harvest_label(harvest: object) -> str:
    value = str(harvest).strip() if harvest is not None else ""
    if not value:
        return "Não informado"

    try:
        year = int(value)
    except ValueError:
        return value

    return f"{year}/{year + 1}"


def text_or_default(
    value: object | None,
    *,
    default: str = "Não informado",
) -> str:
    text = str(value).strip() if value is not None else ""
    return text or default


def format_document_number(
    value: object | None,
    *,
    default: str = "Não informado",
) -> str:
    raw = "".join(char for char in str(value or "") if char.isdigit())
    if len(raw) == 11:
        return f"{raw[:3]}.{raw[3:6]}.{raw[6:9]}-{raw[9:]}"
    if len(raw) == 14:
        return f"{raw[:2]}.{raw[2:5]}.{raw[5:8]}/{raw[8:12]}-{raw[12:]}"
    return text_or_default(value, default=default)


def format_zip_code(
    value: object | None,
    *,
    default: str = "Não informado",
) -> str:
    raw = "".join(char for char in str(value or "") if char.isdigit())
    if len(raw) != 8:
        return text_or_default(value, default=default)
    return f"{raw[:5]}-{raw[5:]}"


def format_address_line(
    street: object | None,
    number: object | None,
    complement: object | None = None,
    *,
    default: str = "Não informado",
) -> str:
    street_text = str(street).strip() if street else ""
    number_text = str(number).strip() if number else ""
    complement_text = str(complement).strip() if complement else ""

    if street_text and number_text and complement_text:
        return f"{street_text}, {number_text} - {complement_text}"
    if street_text and number_text:
        return f"{street_text}, {number_text}"
    if street_text and complement_text:
        return f"{street_text} - {complement_text}"
    if street_text:
        return street_text
    return default


def format_city_state(
    city: object | None,
    state: object | None,
    *,
    default: str = "Não informado",
) -> str:
    city_text = str(city).strip() if city else ""
    state_text = str(state).strip() if state else ""

    if city_text and state_text:
        return f"{city_text}/{state_text}"
    return city_text or state_text or default


def format_date_br(
    value: date | datetime | None,
    *,
    tz_name: str | None = None,
    default: str = "Não informado",
) -> str:
    if value is None:
        return default

    if isinstance(value, datetime):
        if tz_name and value.tzinfo is not None:
            return value.astimezone(ZoneInfo(tz_name)).strftime("%d/%m/%Y")
        return value.strftime("%d/%m/%Y")

    return value.strftime("%d/%m/%Y")


def polygon_centroid(coordinates: list[tuple[float, float]]) -> tuple[float, float]:
    if not coordinates:
        return (0.0, 0.0)

    lat_sum = 0.0
    lon_sum = 0.0
    for lat, lon in coordinates:
        lat_sum += lat
        lon_sum += lon

    size = len(coordinates)
    return (lat_sum / size, lon_sum / size)


def format_dms_coordinates(latitude: float, longitude: float) -> str:
    return f"{_to_dms(latitude, is_latitude=True)}, {_to_dms(longitude, is_latitude=False)}"


def format_coordinates(latitude: float, longitude: float) -> str:
    return f"{latitude:.6f}, {longitude:.6f}"


def format_state(value: str | None) -> str:
    if not value:
        return ""

    state_code = value.strip().upper()
    if state_code in procurement.BrazilianStateDisplayNames.__members__:
        return procurement.BrazilianStateDisplayNames[state_code].value

    return value


def _to_dms(value: float, *, is_latitude: bool) -> str:
    direction = "N" if is_latitude else "E"
    if value < 0:
        direction = "S" if is_latitude else "W"

    absolute = abs(value)
    degrees = int(absolute)
    minutes_float = (absolute - degrees) * 60
    minutes = int(minutes_float)
    seconds = int(round((minutes_float - minutes) * 60))

    if seconds == 60:
        seconds = 0
        minutes += 1
    if minutes == 60:
        minutes = 0
        degrees += 1

    return f"{degrees:02d}°{minutes:02d}'{seconds:02d}\"{direction}"
