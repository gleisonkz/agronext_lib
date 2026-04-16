from ...schemas import ProponentDeclarationData


def build_proposal_proponent_declaration() -> ProponentDeclarationData:
    content_html = """
<p>Declaro, sob minha responsabilidade profissional, que:</p>
<p><strong>• Identificação e Representação </strong>- Atuo nesta contratação como corretor devidamente registrado na SUSEP e, quando aplicável, como representante do proponente, nos termos da lei.</p>
<p><strong>• Entrega da Proposta </strong>- Entreguei ao proponente, em suporte duradouro, a proposta completa com as condições aplicáveis e informei o prazo legal para análise pela seguradora.</p>
<p><strong>• Orientação Básica </strong>- Esclareci ao proponente a importância de responder ao questionário de risco, quando houver, de forma completa e verdadeira, alertando sobre as consequências legais de omissões ou informações falsas.</p>
""".strip()

    checkbox_text = (
        "Eu me responsabilizo e declaro estar formalmente autorizado e/ou ser o responsável legal, "
        "pelo titular destes dados pessoais a fornecê-los a Essor."
    )

    return ProponentDeclarationData(
        content_html=content_html,
        content_bold=False,
        checkbox_text=checkbox_text,
        checkbox_checked=True,
        checkbox_align="center",
        checkbox_bold=True,
    )
