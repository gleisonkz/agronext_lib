_GENERAL_INFO_BODY = (
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
    "<li>As condições gerais para o seguro agrícola podem ser encontradas em: <a href=\"https://essor.com.br/condicoes-gerais/\">https://essor.com.br/condicoes-gerais/</a></li></ul>"
)

def build_simulation_general_info_html(text: str | None) -> str:
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
