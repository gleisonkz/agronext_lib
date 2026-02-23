import agronext_procurement as procurement
import agronext_procurement_repositories as repositories
from agronext_procurement.views.common import CoverageDetailsView

from ...constants import PDF_LOGO
from ...schemas import HeaderData


def build_quotation_header(
    view: procurement.QuotationView,
    metadata: repositories.QuotationMetadata,
    coverage: CoverageDetailsView,
) -> HeaderData:
    # Header
    header_data = HeaderData(
        logo_path="",
        main_coverage="101 - Granizo (Pêra)",
        validity_period="",
        reception_date="",
        crop="",
        bacen_code="4304606",  # banco central
        harvest="",
        # Sempre essor
        insurer="ESSOR SEGUROS S.A.",
        insurer_cnpj="14.525.684/0001-50",
        susep="",
        mapa_code="12",
        # Apos a emissao da proposta
        proposal_number="",
        policy="",
    )
    if coverage:
        header_data.logo_path = str(PDF_LOGO.absolute())
        header_data.reception_date = metadata.transmitted_at.strftime("%d/%m/%Y") if metadata.transmitted_at else ""
        header_data.crop = str(coverage.conditions.crop.crop.value)
        header_data.harvest = str(metadata.harvest)
        header_data.susep = str(coverage.susep_code)
        header_data.validity_period = coverage.term.start_date.strftime("%d/%m/%Y") + " - " + coverage.term.end_date.strftime("%d/%m/%Y")

    return header_data
