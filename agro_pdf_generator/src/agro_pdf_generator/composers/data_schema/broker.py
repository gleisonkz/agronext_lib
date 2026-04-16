import re

from ...schemas import BrokerData


_TRAILING_PARENTHESIS_PATTERN = re.compile(r"\s*\([^()]*\)\s*$")


def _strip_trailing_phone_tags(value: str) -> str:
    cleaned = value.strip()
    # Remove trailing tags like "(Celular/ WhatsApp)" while preserving area-code prefix.
    while True:
        updated = _TRAILING_PARENTHESIS_PATTERN.sub("", cleaned)
        if updated == cleaned:
            return cleaned
        cleaned = updated.rstrip()


def _extract_phone_parts(phone_item: object) -> dict:
    if isinstance(phone_item, dict):
        return {
            "contact": str(
                phone_item.get("contact")
                or phone_item.get("phone")
                or phone_item.get("number")
                or ""
            ),
            "type_hint": str(
                phone_item.get("phone_type")
                or phone_item.get("type")
                or phone_item.get("communication_type_description")
                or ""
            ),
            "is_whatsapp": phone_item.get("is_whatsapp"),
            "is_primary": bool(phone_item.get("is_primary")),
        }

    text = str(phone_item).strip() if phone_item is not None else ""
    return {
        "contact": text,
        "type_hint": text,
        "is_whatsapp": None,
        "is_primary": False,
    }


def _format_phone_number(value: object) -> str:
    text = str(value).strip() if value is not None else ""
    if not text or text.lower() == "não informado":
        return "Não informado"

    cleaned = _strip_trailing_phone_tags(text)
    digits = "".join(char for char in cleaned if char.isdigit())

    if digits.startswith("55") and len(digits) in {12, 13}:
        digits = digits[2:]

    if len(digits) == 11:
        return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"

    if len(digits) == 10:
        return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"

    return cleaned


def _resolve_base_tag(phone_number: str, type_hint: str) -> str:
    hint = (type_hint or "").strip().lower()
    if "fix" in hint or "land" in hint:
        return "fixo"
    if "cel" in hint or "mobi" in hint:
        return "celular"

    digits = "".join(char for char in phone_number if char.isdigit())
    return "celular" if len(digits) == 11 else "fixo"


def _resolve_whatsapp(type_hint: str, is_whatsapp: object) -> bool:
    if isinstance(is_whatsapp, bool):
        return is_whatsapp

    hint = (type_hint or "").strip().lower()
    return "whats" in hint


def _format_phone_with_tag(
    value: object,
    *,
    type_hint: str = "",
    is_whatsapp: object = None,
) -> str:
    phone_number = _format_phone_number(value)
    if phone_number == "Não informado":
        return phone_number

    base_tag = _resolve_base_tag(phone_number, type_hint)
    if _resolve_whatsapp(type_hint, is_whatsapp):
        return f"{phone_number} ({base_tag}/whatsapp)"

    return f"{phone_number} ({base_tag})"


def _build_phone_list(broker_details: dict, fallback_phone: str) -> list[str]:
    raw_phones = broker_details.get("phones")
    if isinstance(raw_phones, list) and raw_phones:
        tagged_phones = []
        for item in raw_phones:
            parts = _extract_phone_parts(item)
            tagged_phones.append(
                _format_phone_with_tag(
                    parts["contact"],
                    type_hint=parts["type_hint"],
                    is_whatsapp=parts["is_whatsapp"],
                )
            )
        return tagged_phones

    return [
        _format_phone_with_tag(
            fallback_phone,
            type_hint=str(
                broker_details.get("phone_type")
                or broker_details.get("communication_type_description")
                or ""
            ),
            is_whatsapp=broker_details.get("is_whatsapp"),
        )
    ]


def _resolve_primary_phone(broker_details: dict) -> str:
    direct_phone = broker_details.get("phone")
    if direct_phone:
        return _format_phone_number(direct_phone)

    raw_phones = broker_details.get("phones")
    if isinstance(raw_phones, list) and raw_phones:
        parsed = [_extract_phone_parts(item) for item in raw_phones]
        primary_item = next((item for item in parsed if item["is_primary"]), parsed[0])
        return _format_phone_number(primary_item["contact"])

    return "Não informado"


def build_broker(broker_details: dict) -> BrokerData:
    # Broker
    phone = _resolve_primary_phone(broker_details)
    phones = _build_phone_list(broker_details, phone)

    broker_data = BrokerData(
        name=broker_details.get("trade_name") or "Não informado",
        susep=broker_details.get("susep_code") or "Não informado",
        social_name=broker_details.get("preferred_name") or "Não informado",
        commission_pct="0.0%",
        phone=phone,
        emails=[broker_details.get("email") or "Não informado"],
        phones=phones,
    )

    return broker_data
