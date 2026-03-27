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
        main_coverage="101 - Granizo (Pêra)",
        validity_period="",
        reception_date=metadata.transmitted_at.strftime("%d/%m/%Y") if metadata.transmitted_at else "",
        crop="",
        bacen_code="4304606",  # banco central
        harvest=str(metadata.harvest),
        # Sempre essor
        insurer="ESSOR SEGUROS S.A.",
        insurer_cnpj="14.525.684/0001-50",
        susep="15414.004513/2012-47",
        mapa_code="12",
        # Apos a emissao da proposta
        proposal_number=str(proposal_number) or "",
        policy=str(policy_id) or "",
    )
    if coverage:
        
        header_data.crop = repositories.CROP_TAXONOMY_DICT.get(coverage.conditions.crop.crop, "")
        header_data.susep = str(coverage.susep_code)
        header_data.validity_period = coverage.term.start_date.strftime("%d/%m/%Y") + " - " + coverage.term.end_date.strftime("%d/%m/%Y")

    return header_data


