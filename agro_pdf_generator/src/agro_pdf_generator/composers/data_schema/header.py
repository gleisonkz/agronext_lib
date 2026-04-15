import agronext_procurement as procurement
import agronext_procurement_repositories as repositories
from agronext_procurement.views.common import CoverageDetailsView

from ...constants import PDF_LOGO
from ...schemas import HeaderData


def build_header(
    view: procurement.QuotationView,
    metadata: repositories.QuotationMetadata,
    coverage: CoverageDetailsView,
    policy_id: str | None,
    proposal_number: str | None,
) -> HeaderData:
    # Header
    header_data = HeaderData(
        logo_path=str(PDF_LOGO.absolute()),
        main_coverage="Pera - Granizo",
        validity_period="",
        reception_date=metadata.transmitted_at.strftime("%d/%m/%Y - Hora: %H:%M") if metadata.transmitted_at else "",
        crop="",
        bacen_code="4304606",  # banco central
        harvest= f"{metadata.harvest}/{int(metadata.harvest) + 1}",
        # Sempre essor
        insurer="ESSOR SEGUROS S.A.",
        insurer_cnpj="14.525.684/0001-50",
        susep="15414.004513/2012-47",
        mapa_code="12",
        # Apos a emissao da proposta
        proposal_number=str(proposal_number) if proposal_number is not None else "Não informado",
        policy=str(policy_id) if policy_id is not None else "Não informado",
    )
    if coverage:
        header_data.crop = repositories.CROP_TAXONOMY_DICT.get(coverage.conditions.crop.crop, "")
        header_data.validity_period = "Das 24 horas do dia " + coverage.term.start_date.strftime("%d/%m/%Y") + " até às 24 horas do dia " + "31/05/2027"

    return header_data


