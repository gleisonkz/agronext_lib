import agronext_procurement as procurement

from ...schemas import AuthorizationBeneficiaryData, AuthorizationTermData

DISCHARD_TEXT = "Com a efetivação do crédito em conta corrente ou ordem de pagamento, prometo outorgar à Essor Seguros S/A, plena, geral e irrevogável quitação de valores e direitos, para nada mais reclamar, em juízo ou fora dele, atinente à relação jurídica entabulada entre as partes."
LIABILITY_TEXT = "Declaro que a insuficiência e/ou inexatidão de quaisquer informações prestadas no presente instrumento acarretará a total isenção de responsabilidade da seguradora em relação a prejuízo(s) ou dano(s) dela(s) decorrente(s), direto(s) e/ou indireto(s), ainda que exclusivamente moral, além da inexigibilidade de juros e/ou correção monetária sobre os respectivos valores, pela inexistência de mora no creditamento das importâncias eventualmente devidas (artigo 396 do Código Civil Brasileiro)."
RATIFICATION_TEXT = (
    "Firmo ratifico os termos do presente instrumento para todos os fins legais."
)


def build_proposal_authorization_term(
    view: procurement.ProposalView,
    proposal_number: str,
) -> AuthorizationTermData:
    authorization_text = "Nessa situação, autorizo a seguradora a efetuar o pagamento de qualquer indenização, restituição ou devolução de prêmio através de transferência de crédito que ficará disponível para ser sacado no Banco indicado, de minha escolha:"

    if isinstance(view.applicant, procurement.NPApplicantView):
        applicant_name = view.applicant.identity.full_name
    elif isinstance(view.applicant, procurement.LEApplicantView):
        applicant_name = view.applicant.identity.trade_name
    else:
        applicant_name = ""

    banking_details = view.applicant.banking_details if view.applicant else None

    agency_number = ""
    agency_digit = ""
    account_number = ""
    account_digit = ""

    if banking_details:
        agency_parts = banking_details.agency.split("-", 1)
        agency_number = agency_parts[0]
        agency_digit = agency_parts[1] if len(agency_parts) > 1 else ""

        account_parts = banking_details.account_number.split("-", 1)
        account_number = account_parts[0]
        account_digit = account_parts[1] if len(account_parts) > 1 else ""

    return AuthorizationTermData(
        applicant_name=applicant_name,
        proposal_number=proposal_number,
        has_account="Sim" if banking_details else "Não",
        authorization_text=authorization_text,
        bank_name=banking_details.bank_code if banking_details else "",
        agency_number=agency_number,
        agency_digit=agency_digit,
        account_number=account_number,
        account_digit=account_digit,
        account_type=banking_details.account_type if banking_details else "",
        joint_account=(
            "Sim" if banking_details and banking_details.joint_account else "Não"
        ),
        discharge_text=DISCHARD_TEXT,
        liability_text=LIABILITY_TEXT,
        ratification_text=RATIFICATION_TEXT,
    )


def build_proposal_beneficiary_authorization(
    beneficiaries: list[procurement.NPBeneficiaryView | procurement.LEBeneficiaryView]
    | None,
) -> AuthorizationBeneficiaryData:
    authorization_text = "Nessa situação, autorizo que o crédito referente ao pagamento de qualquer restituição ou devolução de prêmio atinente ao seguro proposto seja efetuado em conta bancária de titularidade do beneficiário da garantia, conforme dados abaixo indicado, de minha responsabilidade."
    observation_text = "*É obrigatória a manifestação de vontade do próprio proponente para autorizar o crédito na conta de beneficiário, sendo expressamente vedada esta declaração por terceiros (incluindo corretor de seguros)."

    if not beneficiaries:
        return AuthorizationBeneficiaryData()

    premium_refund_beneficiary = next(
        (beneficiary for beneficiary in beneficiaries if beneficiary.premium_refund),
        None,
    )
    if premium_refund_beneficiary is None:
        return AuthorizationBeneficiaryData()

    if isinstance(premium_refund_beneficiary, procurement.NPBeneficiaryView):
        beneficiary_full_name = premium_refund_beneficiary.identity.full_name
        beneficiary_cpf = premium_refund_beneficiary.identity.cpf.number
    else:
        beneficiary_full_name = premium_refund_beneficiary.identity.trade_name
        beneficiary_cpf = premium_refund_beneficiary.identity.cnpj.number

    banking_details = premium_refund_beneficiary.banking_details

    agency_number = ""
    agency_digit = ""
    account_number = ""
    account_digit = ""

    if banking_details:
        agency_parts = banking_details.agency.split("-", 1)
        agency_number = agency_parts[0]
        agency_digit = agency_parts[1] if len(agency_parts) > 1 else ""

        account_parts = banking_details.account_number.split("-", 1)
        account_number = account_parts[0]
        account_digit = account_parts[1] if len(account_parts) > 1 else ""

    return AuthorizationBeneficiaryData(
        beneficiary_name=beneficiary_full_name,
        proposal_number="",
        authorization_question="Autoriza o pagamento ou devolução de crédito em conta bancária do beneficiário da garantia?",
        authorization_answer="Sim",
        authorization_text=authorization_text,
        beneficiary_full_name=beneficiary_full_name,
        beneficiary_cpf=beneficiary_cpf,
        beneficiary_relationship=premium_refund_beneficiary.relationship_to_applicant,
        bank_name=banking_details.bank_code if banking_details else "",
        agency_number=agency_number,
        agency_digit=agency_digit,
        account_number=account_number,
        account_digit=account_digit,
        account_type=banking_details.account_type if banking_details else "",
        joint_account=(
            "Sim" if banking_details and banking_details.joint_account else "Não"
        ),
        pix_type="",
        pix_key="",
        observation_text=observation_text,
        discharge_text=DISCHARD_TEXT,
        liability_text=LIABILITY_TEXT,
        ratification_text=RATIFICATION_TEXT,
    )
