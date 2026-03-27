from ...schemas import ApplicantData, LgpdConsentData


def build_lgpd_consent(applicant: ApplicantData) -> LgpdConsentData:
    # TODO
    return LgpdConsentData(
        title="SEGURADO",
        consent_text=(
            "Eu autorizo a Essor a utilizarem meus dados pessoais e imagem para fins comerciais, jurídicos, financeiros e administrativos, inclusive enviarem para empresas terceiras que fazem parte do processo. Esta autorização terá prazo de validade de 15 anos, para garantir que todos os serviços e benefícios ofertados possam ser usufruídos."
        ),
        signature_name=applicant.name,
        signature_cpf=applicant.cpf,
    )
