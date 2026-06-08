import agronext_procurement_repositories as repositories

from ...schemas import RiskQuestionItem, RiskQuestionnaireData


def build_risk_questionnaire(
    metadata: repositories.QuotationMetadata,
) -> RiskQuestionnaireData:
    # Risk questionnaire
    another_insurance_question = RiskQuestionItem(
        question="Existe Outro Seguro Contratado Para a Mesma Área?",
        answer="Não",
    )
    if metadata.another_insurance:
        another_insurance_question.answer = "Sim"
        another_insurance_question.extra_fields = [
            ("Seguradora", metadata.another_insurance_company),
            ("Número da Apólice", metadata.another_insurance_policy_number),
        ]
    else:
        another_insurance_question.answer = "Não"

    pre_existing_damages_question = RiskQuestionItem(
        question="Existem Danos de Pelo Menos Um dos Eventos Cobertos na Safra Atual?",
    )
    if metadata.pre_existing_damage:
        pre_existing_damages_question.answer = "Sim"
    else:
        pre_existing_damages_question.answer = "Não"

    all_land_declared_question = RiskQuestionItem(
        question="As Áreas Declaradas Nas Unidades Seguradas da Proposta Representam Toda a Área Cultivada Desta Cultura na Propriedade?",
    )
    if metadata.all_land_declared:
        all_land_declared_question.answer = "Sim"
    else:
        land_not_declared_reason = metadata.land_not_declared_reason or "Não informado"
        normalized_reason = land_not_declared_reason.strip().casefold()

        extra_fields = [("Motivo", land_not_declared_reason)]
        if normalized_reason == "essor":
            extra_fields.append(
                (
                    "Informe o número do contrato",
                    metadata.another_insurance_policy_number or "Não informado",
                )
            )
        elif normalized_reason in {"proagro", "arrendamento", "contrato de arrendamento"}:
            # Proagro and Arrendamento do not require an additional detail field.
            pass
        else:
            extra_fields.append(
                (
                    "Nome da Seguradora",
                    metadata.other_insurance_company_name or "Não informado",
                )
            )

        all_land_declared_question.answer = "Não"
        all_land_declared_question.extra_fields = extra_fields

    other_culture_lands_question = RiskQuestionItem(
        question="O Proponente Possui Outra Lavoura/Pomar Desta Cultura no Mesmo Município?",
    )
    if metadata.another_plot_same_crop:
        other_culture_lands_question.answer = "Sim"
        other_culture_lands_question.extra_fields = [
            ("Distância", metadata.another_plot_range.replace("-", " ") if metadata.another_plot_range else "Não informado"),
        ]
    else:
        other_culture_lands_question.answer = "Não"

    conservation_unit_question = RiskQuestionItem(
        question="Alguma parcela/talhão da área segurada está total ou parcialmente localizada em Unidade de Conservação (Federal/Estadual/Municipal), Áreas de Preservação Ambiental (exceto se houver aprovação oficial constante em plano de manejo), Área de Preservação Permanente, Reserva Legal, Área embargada por órgão ambiental (IBAMA, ICMBio ou órgão estadual/municipal), Terra Indígena, Território Quilombola ou qualquer área restrita, protegida ou embargada? (Estas informações são relevantes para a aceitação e precificação do seguro, conforme o art. 44 da Lei nº 15.040/2024. Omissões ou inexatidões podem implicar recusa da proposta, revisão de condições ou outras medidas previstas em lei e no contrato.)",
        answer="Sim" if metadata.esg_compliant else "Não",
    )

    risk_questionnaire_data = RiskQuestionnaireData(
        attention_title="Atenção:",
        attention_text=(
            "É fundamental que todas as informações fornecidas na formação do contrato de seguro sejam completas e "
            "precisas. O descumprimento do dever de informar pode resultar na perda de direitos ou na anulação do "
            "contrato de seguro. Caso tenha dúvidas sobre quais informações são relevantes, consulte nosso atendimento"
        ),
        questions=[
            another_insurance_question,
            pre_existing_damages_question,
            all_land_declared_question,
            other_culture_lands_question,
            conservation_unit_question,
        ]
    )
    return risk_questionnaire_data
