from ...schemas import ProponentDeclarationData


def build_proposal_proponent_declaration() -> ProponentDeclarationData:
    content_html = """
<p><strong>DECLARO</strong> que tomei ciência das Condições dos Programas de Subvenção ao Prêmio do Seguro dos Governos Federal e Estadual e <strong>ESTOU DE ACORDO COM SUAS CONDIÇÕES.</strong></p>
<p>Se, por qualquer motivo, o Governo Federal e/ou Estadual não conceda subsídio ao prêmio para esta proposta, <strong>ME RESPONSABILIZO PELO CUSTO INTEGRAL DO SEGURO.</strong></p>
<p><strong>DECLARO</strong> ter ciência e <strong>CONCORDO</strong> com as Condições Gerais deste seguro, para as quais não tenho dúvidas, acatando-as como parte integrante desta proposta.</p>
<p>O proponente, por si, seus sócios, diretores, empregados, agentes prepostos, e outras pessoas que venham a agir em seu nome, direta e indiretamente, <strong>DECLARA</strong> que tem conhecimento do Código de Conduta da Essor disponível no site ("https://essor.com.br/") e, ainda, que se absterá da prática de violações aos direitos humanos, bem como cumprirá quaisquer legislação, regulamentações e normativos aplicáveis à proteção e respeito a estes direitos na condução de suas atividades, sob pena de cancelamento da apólice e perda de direito à indenização nos termos das condições deste contrato de seguro.</p>
<p><strong>CONFIRMO COMO VERDADEIRAS, COMPLETAS E EXATAS</strong> todas as declarações que prestei a esta proposta, seja a respeito do objeto, como das circunstâncias, <strong>SOB PENA DE PERDA DO DIREITO À GARANTIA</strong>, além de ficar obrigado ao pagamento do prêmio vencido (Art. 766 do Código Civil).</p>
<p><strong>COMPROMETO-ME</strong> a comunicar à Seguradora qualquer alteração relativa ao seguro assim que ocorra e estou ciente de que esse fato será objeto de nova análise por parte da Seguradora, podendo resultar em ajuste de prêmio ou até mesmo cancelamento do seguro. Estas informações poderão ser auditadas pela Seguradora.</p>
<p>Tenho ciência dos anexos a esta Proposta, <strong>CUJAS CÓPIAS RECEBI NO ATO DA SUA ASSINATURA, ACEITANDO-OS NA ÍNTEGRA.</strong></p>
<p><strong>Tenho ciência de que não terei direito à indenização se estiver em atraso no pagamento do prêmio</strong>, se o sinistro ocorrer antes da quitação das parcelas vencidas e não pagas (Art. 763 do Código Civil).</p>
<p><strong>AUTORIZO</strong> o uso de meio eletrônico pela Seguradora para o contato e envio de informações referentes ao seguro, inclusive envio de apólices e boletos.</p>
<p>Solicito cobertura provisória de seguro, que se inicia conforme vigência especificada nesta presente proposta, e estou ciente de que a mesma está condicionada ao pagamento antecipado de prêmio, total ou parcial.</p>
""".strip()

    checkbox_text = (
        "Eu me responsabilizo e declaro estar formalmente autorizado e/ou ser o responsável legal, "
        "pelo titular destes dados pessoais a fornecê-los a AgroBrasil e Essor para usarem estes dados, "
        "para fins comerciais, jurídicos, financeiros e administrativos, inclusive enviar para empresas "
        "terceiras que fazem parte do processo. Esta autorização terá prazo de validade de 15 anos, "
        "para garantir que todos os benefícios ofertados possam ser usufruídos."
    )

    footer_bordered_text = (
        "Declaro que tenho conhecimento da política de privacidade da ESSOR "
        "(https://www.essor.com.br/wp-content/uploads/politica_privacidade_protecao_dados.pdf) "
        "e que estou devidamente autorizado pelo titular destes dados pessoais a compartilhá-los com a Essor, "
        "para que esta possa tratá-los em conformidade com a política mencionada, responsabilizando-me "
        "pelas informações prestadas."
    )

    return ProponentDeclarationData(
        content_html=content_html,
        content_bold=False,
        checkbox_text=checkbox_text,
        checkbox_checked=True,
        checkbox_align="center",
        checkbox_bold=True,
        left_label="Local e data:",
        center_label="Assinatura do proponente:",
        right_label="Assinatura do corretor:",
        observation_text="Assinatura opcional. Informações foram validadas através de autenticação em sistema.",
        footer_bordered_text=footer_bordered_text,
    )
