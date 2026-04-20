from zoneinfo import ZoneInfo

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
    logo_path: str | None = None,
) -> HeaderData:
    reception_date = ""
    if metadata.created_at:
        reception_date = metadata.created_at.astimezone(ZoneInfo("America/Sao_Paulo"))
        reception_date = reception_date.strftime("%d/%m/%Y - Hora: %Hh%M")

    # Header
    header_data = HeaderData(
        logo_path=logo_path or str(PDF_LOGO.absolute()),
        main_coverage="Pera - Granizo",
        validity_period="",
        reception_date=reception_date,
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


