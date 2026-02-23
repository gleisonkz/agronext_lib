from datetime import datetime, timedelta


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
