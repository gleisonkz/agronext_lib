import agronext_procurement as procurement


_GENERAL_INFO_BODY = (
    "<p> </p>"
    "<p> </p>"
    "<p> </p>"
    "<p> </p>"
    "<ul><li>SIMULAÇÃO DE SEGURO E SEUS EFEITOS. Este processo consiste apenas em simulação do valor"
    "do prêmio com base em informações preliminares e serve como referência para o custo do seguro.</li>"
    "<li>A SIMULAÇÃO DE SEGURO JUNTO À SEGURADORA NÃO EQUIVALE À PROPOSTA. Assim, a fixação pela Seguradora do valor definitivo do prêmio, "
    "bem como aceitação, ou recusa, do risco fica condicionada à apresentação pelo proponente, seu representante legal, ou seu corretor de seguros, "
    "da proposta de seguro com todas as informações necessárias, elementos necessários para a análise do "
    "risco e a fixação do prêmio definitivo. Com base nessas informações, "
    "a proposta de seguro poderá ser aceita ou não. O valor definitivo do prêmio será validado no momento da contratação do seguro.</li>"
    "<li>PARA EFETIVAR O SEGURO AGRÍCOLA, ENTRE EM CONTATO COM SEU CORRETOR DE SEGURO E SOLICITE O ENCAMINHAMENTO DA PROPOSTA À SEGURADORA.</li>"
    "<li>A nossa cartilha resumida pode ser encontrada em: <a href=\"https://www.agrobrasilseguros.com.br/#seguros\">https://www.agrobrasilseguros.com.br/#seguros</a></li>"
    "<li>As condições gerais para o seguro agrícola podem ser encontradas em: <a href=\"https://essor.com.br/condicoes-gerais/\">https://essor.com.br/condicoes-gerais/</a></li></ul>"
)


def format_decimal(value: float, precision: int = 2) -> str:
    return f"{value:.{precision}f}".replace(".", ",")


def format_percentage(value: float) -> str:
    return f"{value:.2f}%".replace(".", ",")


def format_phone(value: str | None) -> str:
    if not value:
        return ""

    digits = "".join(char for char in value if char.isdigit())

    if digits.startswith("55") and len(digits) in {12, 13}:
        digits = digits[2:]

    if len(digits) == 11:
        return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"

    if len(digits) == 10:
        return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"

    return value


def format_state(value: str | None) -> str:
    if not value:
        return ""

    state_code = value.strip().upper()
    if state_code in procurement.BrazilianStateDisplayNames.__members__:
        return procurement.BrazilianStateDisplayNames[state_code].value

    return value


def resolve_display_label(raw_value: object | None, mapping: dict) -> str:
    if raw_value is None:
        return ""

    value = getattr(raw_value, "value", raw_value)
    return mapping.get(value, str(value))


def format_coordinates(latitude: float, longitude: float) -> str:
    return f"{latitude:.6f}, {longitude:.6f}"


def build_general_info_html(text: str | None) -> str:
    body = (text or _GENERAL_INFO_BODY).strip()
    return (
        '<div class="sim-general-info" style="text-align: center;">'
        '<style>'
        '.sim-general-info ul { margin: 0 0 0 12px; padding-left: 12px; }'
        '.sim-general-info li { margin-bottom: 4px; }'
        '</style>'
        '<div style="display: inline-block; text-align: left;">'
        f"{body}"
        "</div>"
        "</div>"
    )
