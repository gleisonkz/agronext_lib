from pathlib import Path

import agronext_procurement_repositories as repositories

from ...schemas import (
    FederalSubsidyTermData,
    ModalityOption,
    StateAuthorizationTermData,
    StateSubsidyTermData,
    SubsidyData,
    SubsidyQuestionItem,
)

RESOURCES_DIR = Path(__file__).resolve().parents[4] / "resources"
STATE_AUTHORIZATION_LOGO_PATH = RESOURCES_DIR / "pdf" / "images" / "Logo Parana.png"


def _to_sim_nao(value: bool | None) -> str:
    return "Sim" if value else "Não"


def build_proposal_subsidy_questions(
    quotation_metadata: repositories.QuotationMetadata,
) -> SubsidyData:
    questions = [
        SubsidyQuestionItem(
            question="Solicitou subvenção federal para esta proposta?",
            answer=_to_sim_nao(quotation_metadata.applied_for_federal_subsidy),
        ),
        SubsidyQuestionItem(
            question="Solicitou subvenção estadual para esta proposta?",
            answer=_to_sim_nao(quotation_metadata.applied_for_state_subsidy),
            extra_fields=[
                ("Número do CAD/PRO", quotation_metadata.cadpro or "Não informado")
            ],
        ),
        SubsidyQuestionItem(
            question="Situação no CADIN Federal",
            answer=quotation_metadata.cadin_status or "Não informado",
        ),
    ]

    return SubsidyData(questions=questions)


def build_proposal_state_subsidy_term(
    quotation_metadata: repositories.QuotationMetadata,
) -> StateSubsidyTermData:
    if not quotation_metadata.applied_for_state_subsidy:
        return StateSubsidyTermData()

    intro_text = (
        "Pelo presente Termo, eu, ______________________________________, produtor(a) rural, "
        f"inscrito(a) no Cadastro do Produtor Rural (CAD/PRO) sob nº {quotation_metadata.cadpro or '________________'}, "
        "na condição de beneficiário(a) da Subvenção Econômica estadual ao prêmio do seguro rural, "
        "na modalidade __________________________ (indicar agrícola, pecuário ou florestal e o tipo de cobertura), "
        "para a cultura/atividade __________________________, declaro que:"
    )

    declarations = [
        "I - Atender a todos os requisitos, referente ao exercício de 2024, para fazer jus à Subvenção Econômica estadual ao prêmio do seguro rural, as regras estabelecidas na Lei nº 16.166/09, regulamentada pelo Decreto nº 3.375/2019, os normativos aprovados pelo Comitê Gestor para a Subvenção ao Prêmio de Seguro Rural e homologadas pelo titular da Secretaria de Estado da Agricultura e Abastecimento;",
        "II - Estar adimplente com a Administração Pública Estadual, bem como estar ciente de que será verificada a minha regularidade perante a FOMENTO PARANÁ e ao FDE e, ainda, será verificada minha regularidade junto ao CADIN estadual, e de que, caso haja alguma restrição, não poderei me beneficiar da Subvenção Econômica estadual para o pagamento do prêmio do seguro ao seguro rural;",
        "III - Estar ciente de que não me é permitido receber a Subvenção Econômica ao prêmio do seguro rural, para a mesma atividade e área em que já existe cobertura do Programa de Garantia de Atividade Agropecuária (PROAGRO);",
        "IV - Estar ciente de que a Subvenção Econômica estadual não é complementar à Subvenção Econômica federal, devendo a aplicação do percentual e limite máximo da Subvenção Econômica Estadual observar o valor do prêmio do seguro rural;",
        "V - Para todos os fins de direito, visando o correto enquadramento do seguro rural proposto, estou ciente dos percentuais e valores máximos de Subvenção Estadual para pagamento do prêmio do seguro rural para as culturas aprovadas pelo Comitê Gestor do PSR/PR e homologadas pelo Titular da SEAB;",
        "VI - Estar ciente de que a Subvenção Econômica estadual ao prêmio de seguro rural não poderá exceder o limite de R$ 4.400,00, por CPF/CNPJ, cultura ou espécies animais de R$ 8.800,00, no ano civil;",
        "VII - Estar ciente da obrigatoriedade do cumprimento das recomendações estabelecidas nas portarias de Zoneamento Agrícola de Risco Climático (ZARC), publicado pelo Ministério da Agricultura, Pecuária e Abastecimento - MAPA;",
        "VIII - Estar ciente das hipóteses de cancelamento das operações de seguro rural, previstas no Decreto nº 3.375/2019, e que sendo o responsável pela situação de irregularidade que determinou o cancelamento, ficarei impedido(a) de participar do programa de subvenção econômica pelo prazo legal e terei que restituir ao Fundo de Desenvolvimento Econômico (FDE), por intermédio da Fomento do Paraná, o valor da Subvenção Econômica estadual referente à operação, com atualização monetária pela variação da Taxa Selic;",
        "IX - Estar ciente de que as operações subvencionadas serão objeto de fiscalização pela SEAB/DERAL e pela Fomento Paraná ou por entidade pública ou privada por elas designadas, e comprometo-me, desde já, a oferecer as condições necessárias ao desempenho dos trabalhos de fiscalização, permitindo o acesso ao meu empreendimento e, disponibilizando, quando solicitado, os documentos que se fizerem necessários;",
        "X - Para todos os fins de direito, declaro que as informações por mim prestadas no presente Termo e na proposta de seguro são completas e verídicas, não contendo quaisquer omissões ou inexatidões.",
    ]

    return StateSubsidyTermData(
        government_header="GOVERNO DO ESTADO DO PARANÁ. SECRETARIA DE AGRICULTURA E ABASTECIMENTO SEAB DEPARTAMENTO DE ECONOMIA RURAL - DERAL.",
        annex_title="ANEXO III - TERMO DE RESPONSABILIDADE",
        intro_text=intro_text,
        declarations=declarations,
        date_location_text="______________________________, _____ de _____________________ de ________",
        signature_text="Assinatura do Produtor Rural ou Pessoa Jurídica, o que couber",
        name_cpf_text="Nome ______________________________________ - CPF/CNPJ ______________________________________",
    )


def build_proposal_state_authorization_term(
    quotation_metadata: repositories.QuotationMetadata,
) -> StateAuthorizationTermData:
    if not quotation_metadata.applied_for_state_subsidy:
        return StateAuthorizationTermData()

    intro_text = (
        "Pelo presente Termo eu, ______________________________________, produtor(a) rural inscrito(a) no CPF/MF "
        "(CNPJ se for pessoa jurídica) nº ____________________________, portador(a) da Carteira de Identidade nº "
        "____________________________, residente e domiciliado(a) no município de ____________________________, "
        f"com registro no CAD PRO nº {quotation_metadata.cadpro or '________________________'}, expressamente autorizo:"
    )

    declarations = [
        "I - que o pagamento do valor referente à Subvenção Econômica estadual ao Prêmio de Seguro Rural que me foi concedida com recursos do Fundo de Desenvolvimento Econômico do Estado do Paraná (FDE), referente ao seguro rural da proposta, por meio de seu gestor, a Fomento do Paraná, seja feito diretamente à Seguradora Essor Seguros S.A., CNPJ nº 14.525.684/0001-50, com sede no município do Rio de Janeiro, Estado do Rio de Janeiro.",
        "II - Autorizo que o valor total da Subvenção Econômica concedida pelo Estado do Paraná, com recursos do Tesouro estadual, aportados no Fundo de Desenvolvimento Econômico (FDE), ora concedida, seja utilizada exclusivamente para deduzir do valor total do prêmio de seguro rural por mim contratado com a Seguradora Essor Seguros S.A., CNPJ nº 14.525.684/0001-50, com sede no município do Rio de Janeiro, Estado do Rio de Janeiro.",
    ]

    return StateAuthorizationTermData(
        logo_path=str(STATE_AUTHORIZATION_LOGO_PATH),
        government_header="GOVERNO DO ESTADO",
        government_subheader="SECRETARIA DA AGRICULTURA E DO ABASTECIMENTO",
        annex_title="ANEXO IV – TERMO DE AUTORIZAÇÃO",
        intro_text=intro_text,
        declarations=declarations,
        date_location_text="______________________________, ____ de __________________ de ______.",
        signature_text="Assinatura do Produtor Rural ou Pessoa Jurídica, o que couber.",
        name_cpf_text="Nome ______________________________________  CPF ou CNPJ ______________________________________",
    )


def build_proposal_federal_subsidy_term(
    quotation_metadata: repositories.QuotationMetadata,
) -> FederalSubsidyTermData:
    if not quotation_metadata.applied_for_federal_subsidy:
        return FederalSubsidyTermData()

    declarations = [
        "a) Concordo com a fiscalização a ser realizada por preposto do Ministério da Agricultura, Pecuária e Abastecimento – MAPA; autorizo o seu acesso ao empreendimento objeto do seguro rural subvencionado e concordo em oferecer as condições necessárias ao desempenho do trabalho, facultando inclusive o acesso aos documentos relativos ao empreendimento;",
        "b) Estou ciente de que não posso contratar seguro rural, com subvenção econômica do Governo Federal ao prêmio, para a mesma lavoura em que eu for beneficiário do Programa de Garantia da Atividade Agropecuária – PROAGRO. Por isso, informo que a cultura referente a esta proposta, para a qual estou pleiteando a subvenção federal: ( ) Não é beneficiária do PROAGRO; ( ) É beneficiária do PROAGRO, na mesma propriedade rural e, por isso, estou anexando a esta proposta croqui ou documento contendo as coordenadas geográficas da lavoura que deverá ser objeto de subvenção federal;",
        "c) O valor recebido do PSR do Governo Federal, por ano civil, a partir de 1º de janeiro de 2024, não ultrapassa o limite total de R$ 120.000,00 (cento e vinte mil reais) e de R$ 60.000,00 (sessenta mil reais) em cada um dos grupos de atividades de seguro abaixo: 1. Grãos; 2. Frutas, olerícolas, café e cana-de-açúcar; 3. Florestas; 4. Pecuária; 5. Aquicultura;",
        f"d) Estou ciente de que será consultada a minha adimplência junto ao Cadastro Informativo de créditos não quitados do setor público federal (Cadin), em decorrência do disposto no artigo 60 da Lei 10.522, de 19 de julho de 2002, e de que, caso haja alguma restrição, não poderei me beneficiar da subvenção ao prêmio do seguro rural. Situação informada: {quotation_metadata.cadin_status or 'Não informado'};",
        "e) Comprometo-me a cumprir as recomendações estabelecidas nas portarias de zoneamento agrícola de risco climático do MAPA (cultivar, data do plantio e tipo de solo), na forma disciplinada no Plano Trienal do Seguro Rural – PTSR;",
        "f) Caso eu descumpra qualquer condição do Programa e, consequentemente, haja o cancelamento da subvenção federal ao prêmio, estou ciente de que terei de devolver integralmente o valor da subvenção federal acrescido das sanções previstas no Regulamento de Operacionalização da Subvenção;",
        "g) Estou anexando à Proposta de Seguro, para efeito de comprovação de regularidade fiscal (somente para pessoa jurídica ou firma individual): Certificado de Regularidade do FGTS e certidão conjunta dos débitos da Secretaria da Receita Federal e quanto às contribuições sociais;",
        "h) Estou ciente de que esta proposta de seguro não confere direito subjetivo à subvenção federal, pois ainda será submetida ao MAPA, podendo ser aprovada ou reprovada, de acordo com os critérios estabelecidos no PSR, principalmente no que se refere ao limite orçamentário do Programa;",
        "i.1) A contratação desta apólice de seguro rural está vinculada a uma exigência de um contrato de financiamento agrícola? ( ) Não está vinculada; ( ) Sim, está vinculada. Informar o nome da instituição financeira e verificar a Seção II: ________________________________;",
        "i.2) Se sim, foi oferecido ao financiado a escolha entre, no mínimo, duas apólices de diferentes seguradoras, sendo que pelo menos uma delas não poderá ser de empresa controlada, coligada ou pertencente ao mesmo conglomerado econômico-financeiro da credora? ( ) Não foi oferecido; ( ) Sim, foi oferecido. Informar o(s) nome(s) da(s) seguradora(s): ________________________________;",
        "j) As informações por mim prestadas no presente Termo e na Proposta de Seguro são completas e verídicas, não contendo quaisquer omissões ou inexatidões.",
    ]

    return FederalSubsidyTermData(
        ministry_header="MINISTÉRIO DA AGRICULTURA, PECUÁRIA E ABASTECIMENTO",
        committee_text="Comitê Gestor Interministerial do Seguro Rural",
        secretariat_text="Secretaria-Executiva",
        main_title="TERMO DE RESPONSABILIDADE PARA PARTICIPAÇÃO NO PROGRAMA DE SUBVENÇÃO AO PRÊMIO DO SEGURO RURAL",
        section_title="SEÇÃO I (para preenchimento pelo beneficiário):",
        intro_text="Informo que estou ciente de minha responsabilidade como beneficiário do Programa de Subvenção ao Prêmio do Seguro Rural – PSR: a) Na modalidade agrícola, para a cultura de __________________________; b) Na modalidade pecuário; c) Na modalidade florestas; d) Na modalidade aquícola.",
        modality_options=[
            ModalityOption(
                label="Na modalidade agrícola, para a cultura de __________________________",
                checked=False,
            ),
            ModalityOption(label="Na modalidade pecuário", checked=False),
            ModalityOption(label="Na modalidade florestas", checked=False),
            ModalityOption(label="Na modalidade aquícola", checked=False),
        ],
        declaration_intro="Para o correto enquadramento do seguro que estou propondo, DECLARO que:",
        declarations=declarations,
        signature_date_text="Data: ____/____/__________",
        signature_text="Assinatura do Proponente: ____________________________________________",
        section2_title="SEÇÃO II (para preenchimento pelo responsável da instituição financeira onde foi realizado o contrato de financiamento agrícola, se for o caso)",
        section2_question="a) Foi oferecido ao financiado a escolha entre, no mínimo, duas apólices de diferentes seguradoras, sendo que pelo menos uma delas não poderá ser de empresa controlada, coligada ou pertencente ao mesmo conglomerado econômico-financeiro da credora (Lei nº 13.195, de 25 de novembro de 2015)?",
        section2_options=[
            "Não foi oferecido ao financiado a escolha entre, no mínimo, duas apólices de diferentes seguradoras;",
            "Não foi oferecido ao financiado pois o produtor apresentou uma outra apólice de seguro;",
            "Não foi oferecido ao financiado pois não há outra seguradora operando neste município para essa cultura/modalidade;",
            "Sim, foi oferecido ao financiado a escolha entre, no mínimo, duas apólices de diferentes seguradoras. Informar o(s) nome(s) da(s) seguradora(s): ________________________________;",
        ],
        section2_date_text="Data: ____/____/__________",
        section2_responsible_text="Dados do responsável da instituição financeira: Nome completo: _______________________________________________",
        section2_cpf_text="CPF: ________________________________",
        section2_signature_text="Assinatura: ________________________________",
    )
