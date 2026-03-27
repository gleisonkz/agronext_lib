from ...schemas import PoliticalExposureData, ApplicantData


def build_proposal_political_exposure(applicant_data: ApplicantData, has_political_exposure: bool) -> PoliticalExposureData:
    return PoliticalExposureData(
        is_pep="Sim" if has_political_exposure else "Não",
        pep_name=applicant_data.name if has_political_exposure else "Não"
    )
