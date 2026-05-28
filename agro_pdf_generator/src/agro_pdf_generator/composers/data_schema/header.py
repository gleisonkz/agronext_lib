import datetime
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
    is_proposal: bool = False,
) -> HeaderData:
    tz = ZoneInfo("America/Sao_Paulo")
    reception_date = ""
    version_date = ""
    events_version = None
    if metadata.transmitted_at and is_proposal:
        reception_date = metadata.transmitted_at.astimezone(tz)
        reception_date = reception_date.strftime("%d/%m/%Y - Hora: %Hh%M")
    elif metadata.created_at:
        reception_date = metadata.created_at.astimezone(tz)
        reception_date = reception_date.strftime("%d/%m/%Y - Hora: %Hh%M")

    if metadata.version:
        events_version = metadata.version

    if metadata.updated_at:
        version_date = metadata.updated_at.astimezone(tz)
        version_date = version_date.strftime("%d/%m/%Y - Hora: %Hh%M")

    # Header
    header_data = HeaderData(
        logo_path=logo_path or str(PDF_LOGO.absolute()),
        main_coverage="Pera - Granizo",
        validity_period="",
        reception_date=reception_date,
        version=str(events_version) if events_version else "Não informado",
        version_date=version_date or "Não informado",
        crop="",
        bacen_code="11283005",  # Código do Banco central da Pera
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

def build_simulation_header(
    *,
    simulation_date: datetime,
    harvest: int,
    coverage_id: int,
    crop: str,
    peril: str,
    header_logo_path: str | None = None,
) -> HeaderData:
    crop_label = repositories.CROP_TAXONOMY_DICT.get(crop, crop)
    peril_label = repositories.PERIL_TAXONOMY_DICT.get(peril, peril)
    coverage_label = f"{coverage_id} - {peril_label} ({crop_label})"

    return HeaderData(
        logo_path=header_logo_path or str(PDF_LOGO.absolute()),
        reception_date=simulation_date.strftime("%d/%m/%Y"),
        crop=crop_label,
        main_coverage=coverage_label,
        harvest=f"{harvest}/{harvest + 1}",
        bacen_code="11283005",  # Código do Banco central da Pera
        insurer="ESSOR SEGUROS S.A.",
        insurer_cnpj="14.525.684/0001-50",
        susep="15414.004513/2012-47",
        mapa_code="12",
    )


