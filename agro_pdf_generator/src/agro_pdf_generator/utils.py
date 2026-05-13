from datetime import datetime, timedelta

from agronext_procurement.views.common import PhoneView


def format_monetary_value(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def next_month(date: datetime) -> datetime:
    month = date.month + 1 if date.month < 12 else 1
    year = date.year if date.month < 12 else date.year + 1
    try:
        new_date = date.replace(year=year, month=month)
    except ValueError:
        # If the day doesn't exist in the new month, set it to the last day of that month
        new_date = date.replace(year=year, month=month + 1, day=1) - timedelta(days=1)
    return new_date


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
