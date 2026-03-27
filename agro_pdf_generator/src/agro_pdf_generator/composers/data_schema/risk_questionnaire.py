import agronext_procurement_repositories as repositories

from ...schemas import RiskQuestionItem, RiskQuestionnaireData


def build_risk_questionnaire(
    metadata: repositories.QuotationMetadata,
) -> RiskQuestionnaireData:
    # Risk questionnaire
    another_insurance_question = RiskQuestionItem(
        question="Existe outro seguro contratado para a mesma área?",
        answer="Não",
    )
    if metadata.another_insurance:
        another_insurance_question.answer = "Sim"
        another_insurance_question.extra_fields = [
            ("Seguradora", metadata.another_insurance_company),
            ("Número da apólice", metadata.another_insurance_policy_number),
        ]
    else:
        another_insurance_question.answer = "Não"

    pre_existing_damages_question = RiskQuestionItem(
        question="Existem danos de pelo menos um dos eventos cobertos na safra atual?",
    )
    if metadata.pre_existing_damage:
        pre_existing_damages_question.answer = "Sim"
    else:
        pre_existing_damages_question.answer = "Não"

    all_land_declared_question = RiskQuestionItem(
        question="As áreas declaradas nas unidades seguradas da proposta representam toda a área cultivada desta cultura na propriedade?",
    )
    if metadata.all_land_declared:
        all_land_declared_question.answer = "Sim"
    else:
        all_land_declared_question.answer = "Não"

    other_culture_lands_question = RiskQuestionItem(
        question="O proponente possui outra lavoura/pomar desta cultura no mesmo município?",
    )
    if metadata.another_plot_same_crop:
        other_culture_lands_question.answer = "Sim"
    else:
        other_culture_lands_question.answer = "Não"

    conservation_unit_question = RiskQuestionItem(
        question="Alguma parcela/talhão da área segurada está total ou parcialmente localizada em Unidade de Conservação (Federal/Estadual/Municipal), Áreas de Preservação Ambiental (exceto se houver aprovação oficial constante em plano de manejo), Área de Preservação Permanente, Reserva Legal, Área embargada por órgão ambiental (IBAMA, ICMBio ou órgão estadual/municipal), Terra Indígena, Território Quilombola ou qualquer área restrita, protegida ou embargada? (Estas informações são relevantes para a aceitação e precificação do seguro, conforme o art. 44 da Lei nº 15.040/2024. Omissões ou inexatidões podem implicar recusa da proposta, revisão de condições ou outras medidas previstas em lei e no contrato.)",
        answer="Sim" if metadata.esg_compliant else "Não",
    )

    risk_questionnaire_data = RiskQuestionnaireData(
        questions=[
            another_insurance_question,
            pre_existing_damages_question,
            all_land_declared_question,
            other_culture_lands_question,
            conservation_unit_question,
        ]
    )
    return risk_questionnaire_data
