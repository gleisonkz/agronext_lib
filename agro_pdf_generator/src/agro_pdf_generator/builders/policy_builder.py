from __future__ import annotations

import re
from html import escape
from pathlib import Path

from weasyprint import HTML

from ..schemas import PolicyDocumentData


_PT_BR_MONTH_NAMES = (
    "janeiro",
    "fevereiro",
    "março",
    "abril",
    "maio",
    "junho",
    "julho",
    "agosto",
    "setembro",
    "outubro",
    "novembro",
    "dezembro",
)

_BRAZILIAN_STATE_CATALOG = (
  {"id": 1, "code": "AC"},
  {"id": 2, "code": "AL"},
  {"id": 3, "code": "AP"},
  {"id": 4, "code": "AM"},
  {"id": 5, "code": "BA"},
  {"id": 6, "code": "CE"},
  {"id": 7, "code": "DF"},
  {"id": 8, "code": "ES"},
  {"id": 9, "code": "GO"},
  {"id": 10, "code": "MA"},
  {"id": 11, "code": "MT"},
  {"id": 12, "code": "MS"},
  {"id": 13, "code": "MG"},
  {"id": 14, "code": "PA"},
  {"id": 15, "code": "PB"},
  {"id": 16, "code": "PR"},
  {"id": 17, "code": "PE"},
  {"id": 18, "code": "PI"},
  {"id": 19, "code": "RJ"},
  {"id": 20, "code": "RN"},
  {"id": 21, "code": "RS"},
  {"id": 22, "code": "RO"},
  {"id": 23, "code": "RR"},
  {"id": 24, "code": "SC"},
  {"id": 25, "code": "SP"},
  {"id": 26, "code": "SE"},
  {"id": 27, "code": "TO"},
)

_BRAZILIAN_STATE_CODES_BY_ID = {
    state["id"]: state["code"]
    for state in _BRAZILIAN_STATE_CATALOG
}

_BRAZILIAN_STATE_CODES = {
    state["code"]
    for state in _BRAZILIAN_STATE_CATALOG
}


def build_policy_pdf(
    data: PolicyDocumentData,
    logo_path: str,
    *,
    header_image_path: str | None = None,
    footer_image_path: str | None = None,
    signature_image_path: str | None = None,
    font_path: str | None = None,
) -> bytes:
    logo_uri = _asset_uri(logo_path)
    header_uri = _asset_uri(header_image_path)
    footer_uri = _asset_uri(footer_image_path)
    signature_uri = _asset_uri(signature_image_path)
    font_uri = _asset_uri(font_path)
    bold_font_uri = ""
    if font_uri and font_path:
        base_font_path = Path(font_path)
        bold_candidates = (
            base_font_path.with_name("PTMono-Bold.ttf"),
            base_font_path.with_name("PTMono-Bold.otf"),
        )
        for candidate in bold_candidates:
            if candidate.exists():
                bold_font_uri = candidate.resolve().as_uri()
                break

    risk_chunks = _chunk(data.risk_items, 5)
    legal_contents = _build_legal_page_contents(data, signature_uri)

    total_pages = 2 + len(risk_chunks) + len(legal_contents)

    pages: list[str] = []
    page_number = 1
    pages.append(
        _build_page_one(
            data,
            logo_uri,
            header_uri,
            footer_uri,
            page_number=page_number,
            total_pages=total_pages,
        )
    )
    page_number += 1

    pages.append(
        _build_page_two(
            data,
            logo_uri,
            header_uri,
            footer_uri,
            page_number=page_number,
            total_pages=total_pages,
        )
    )
    page_number += 1

    for chunk in risk_chunks:
        pages.append(
            _build_page_risk(
                data,
                logo_uri,
                header_uri,
                footer_uri,
                page_number=page_number,
                total_pages=total_pages,
                items=chunk,
            )
        )
        page_number += 1

    pages.extend(
        _build_legal_pages(
            data,
            logo_uri,
            header_uri,
            footer_uri,
            legal_contents=legal_contents,
            start_page_number=page_number,
            total_pages=total_pages,
        )
    )

    font_face_css = ""
    font_synthesis_css = "font-synthesis: weight;"
    if font_uri:
        font_face_css = (
            "@font-face {"
            "font-family: 'PTMonoCustom';"
            f"src: url('{font_uri}') format('truetype');"
            "font-weight: 400;"
            "font-style: normal;"
            "}"
        )
        if bold_font_uri:
            font_face_css += (
                "@font-face {"
                "font-family: 'PTMonoCustom';"
                f"src: url('{bold_font_uri}') format('truetype');"
                "font-weight: 600;"
                "font-style: normal;"
                "}"
                "@font-face {"
                "font-family: 'PTMonoCustom';"
                f"src: url('{bold_font_uri}') format('truetype');"
                "font-weight: 700;"
                "font-style: normal;"
                "}"
            )
            font_synthesis_css = "font-synthesis: none;"

    html = f"""<!DOCTYPE html>
<html lang=\"pt-BR\">
<head>
  <meta charset=\"UTF-8\" />
  <style>
    {font_face_css}

    @page {{
      size: A4;
      margin: 0;
    }}

    body {{
      margin: 0;
      font-family: 'PTMonoCustom', 'Courier New', 'Liberation Mono', monospace;
      {font_synthesis_css}
      color: #111;
      font-size: 16px;
      line-height: 1.1;
      font-weight: 400;
      background: #fff;
    }}

    .page {{
      width: 210mm;
      height: 297mm;
      box-sizing: border-box;
      --page-padding-top: 5mm;
      --page-padding-side: 5mm;
      --page-padding-bottom: 4mm;
      --page-indicator-edge-margin: 5mm;
      padding: var(--page-padding-top) var(--page-padding-side) var(--page-padding-bottom);
      position: relative;
      page-break-after: always;
      overflow: hidden;
    }}

    .title-row {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 4px;
      position: relative;
      overflow: visible;
    }}

    .title-row-banner {{
      width: calc(100% + (var(--page-padding-side) * 2));
      margin-top: calc(-1 * var(--page-padding-top));
      margin-left: calc(-1 * var(--page-padding-side));
      margin-right: calc(-1 * var(--page-padding-side));
    }}

    .logo {{
      width: 30mm;
      height: auto;
    }}

    .header-banner {{
      width: 100%;
      height: auto;
      display: block;
      margin-bottom: 2px;
      max-width: none;
      position: relative;
      z-index: 1;
    }}

    .header-center-title {{
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      color: #6f7378;
      font-size: 18px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.2px;
      z-index: 5;
      pointer-events: none;
    }}

    .header-policy-title {{
      position: absolute;
      top: 33%;
      right: 5mm;
      transform: translateY(-50%);
      color: #6f7378;
      font-size: 18px;
      font-weight: 700;
      text-transform: uppercase;
      z-index: 5;
      pointer-events: none;
    }}

    .doc-title {{
      text-align: center;
      font-size: 17px;
      font-weight: 700;
      flex: 1;
      margin-top: 4px;
    }}

    .page-indicator {{
      min-width: 34mm;
      text-align: right;
      font-size: 16px;
      font-weight: 700;
      padding-top: 2px;
      margin-right: calc(var(--page-indicator-edge-margin) - var(--page-padding-side));
    }}

    .line {{
      border-top: 1px solid #333;
      margin: 4px 0;
    }}

    .insurer-line {{
      font-weight: 700;
      font-size: 16px;
      margin-bottom: 2px;
    }}

    .meta-grid {{
      width: 100%;
      border-collapse: collapse;
      table-layout: fixed;
      font-size: 16px;
      margin-top: 3px;
    }}

    .meta-grid td {{
      padding: 1px 4px 1px 0;
      vertical-align: top;
      width: 50%;
      word-break: break-word;
    }}

    .meta-grid .meta-line-compact {{
      white-space: nowrap;
      font-size: 15px;
      letter-spacing: -0.1px;
    }}

    .label {{
      font-weight: 700;
    }}

    .section-title {{
      font-size: 16px;
      font-weight: 700;
      margin: 7px 0 3px 0;
      text-transform: uppercase;
    }}

    .section-box {{
      border-bottom: 1px solid #333;
      padding: 3px 0;
      margin-bottom: 6px;
    }}

    .kv-grid {{
      width: 100%;
      border-collapse: collapse;
      table-layout: fixed;
      margin-bottom: 4px;
    }}

    .kv-grid td {{
      padding: 1px 2px 1px 0;
      vertical-align: top;
      width: 50%;
    }}

    .doc-title,
    .page-indicator,
    .insurer-line,
    .label,
    .section-title,
    .table th,
    .mono-strong {{
      font-family: 'PTMonoCustom', 'Courier New', 'Liberation Mono', monospace;
      font-weight: 700;
    }}

    .page-indicator-banner {{
      position: absolute;
      top: 66%;
      right: var(--page-indicator-edge-margin);
      transform: translateY(-50%);
      background: transparent;
      color: #6f7378;
      min-width: 0;
      padding: 0;
      padding-top: 0;
      font-size: 12px;
      font-weight: 500;
      z-index: 5;
    }}

    .table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 3px;
      margin-bottom: 4px;
    }}

    .table th,
    .table td {{
      border-bottom: 1px solid #555;
      padding: 2px 3px;
      text-align: left;
      vertical-align: top;
    }}

    .coverage-table th,
    .coverage-table td {{
      text-align: center;
      vertical-align: middle;
    }}

    .premium-summary {{
      margin-top: 3px;
      margin-bottom: 6px;
    }}

    .premium-summary-line {{
      padding: 2px 0;
    }}
    .table th {{
      font-weight: 700;
    }}

    .installment-table th,
    .installment-table td {{
      text-align: center;
      vertical-align: middle;
    }}

    .mono-strong {{
      font-weight: 700;
    }}

    .text-block p {{
      margin: 0 0 5px 0;
      text-align: justify;
    }}

    .text-block ul {{
      margin: 3px 0 0 16px;
      padding: 0;
    }}

    .text-block li {{
      margin: 0 0 3px 0;
    }}

    .signature {{
      text-align: center;
    }}

    .signature-near-footer {{
      position: absolute;
      left: var(--page-padding-side);
      right: var(--page-padding-side);
      bottom: 26mm;
      margin-top: 0;
    }}

    .text-block-signature-page {{
      padding-bottom: 60mm;
    }}

    .signature-name {{
      font-size: 30px;
      font-family: 'Brush Script MT', cursive;
      margin-bottom: 2px;
    }}

    .signature-role {{
      font-weight: 700;
      font-size: 16px;
    }}

    .signature-place {{
      margin-top: 10px;
      display: flex;
      justify-content: space-between;
      font-size: 16px;
      width: 75%;
      margin-left: auto;
      margin-right: auto;
    }}

    .signature-place span {{
      white-space: nowrap;
    }}

    .footer {{
      position: absolute;
      left: var(--page-padding-side);
      right: var(--page-padding-side);
      bottom: var(--page-padding-bottom);
      background: #00759b;
      color: #fff;
      font-size: 8px;
      text-align: center;
      padding: 4px 6px;
      line-height: 1.2;
    }}

    .footer-banner {{
      position: absolute;
      left: 0;
      right: 0;
      bottom: 0;
      width: 100%;
      height: auto;
      max-width: none;
      transform: none;
      object-fit: contain;
      object-position: center bottom;
    }}

    .small {{
      font-size: 10px;
    }}

    .signature-image {{
      width: 75mm;
      height: auto;
      margin: 0 auto 2px auto;
      display: block;
    }}
  </style>
</head>
<body>
  {''.join(pages)}
</body>
</html>"""
    html = _preserve_blank_paragraphs(html)

    base_asset_path = _first_existing_path(
        logo_path,
        header_image_path,
        footer_image_path,
        signature_image_path,
        font_path,
    )
    base_url = str(Path(base_asset_path).resolve().parent) if base_asset_path else str(Path.cwd())
    return HTML(string=html, base_url=base_url).write_pdf()


_BLANK_PARAGRAPH_PATTERN = re.compile(r"<p>\s*</p>", flags=re.IGNORECASE)


def _preserve_blank_paragraphs(html: str) -> str:
    # WeasyPrint collapses whitespace-only paragraph content, so replace with NBSP.
    return _BLANK_PARAGRAPH_PATTERN.sub("<p>&nbsp;</p>", html)


def _build_page_one(
    data: PolicyDocumentData,
    logo_uri: str,
    header_uri: str,
    footer_uri: str,
    page_number: int,
    total_pages: int,
) -> str:
    beneficiary_section = ""
    if data.has_beneficiary:
        beneficiaries = list(getattr(data, "beneficiaries", []) or [])
        if beneficiaries:
            section_title = (
                "Dados do Beneficiário"
                if len(beneficiaries) == 1
                else "Dados dos Beneficiários"
            )
            rendered_beneficiaries = []
            for index, beneficiary in enumerate(beneficiaries, start=1):
                heading = ""
                if len(beneficiaries) > 1:
                    heading = (
                        f"<div class=\"mono-strong\" style=\"margin: 2px 0 1px 0;\">"
                        f"Beneficiário {index:02d}</div>"
                    )
                rendered_beneficiaries.append(
                    f"""
  {heading}
  <table class=\"kv-grid\">
    <tr><td colspan=\"2\"><span class=\"label\">Nome/Razão Social:</span> {escape(beneficiary.name)}</td></tr>
    <tr><td colspan=\"2\"><span class=\"label\">Nome Social:</span> {escape(_social_name_or_dash(getattr(beneficiary, "social_name", None)))}</td></tr>
    <tr><td colspan=\"2\"><span class=\"label\">CPF/CNPJ:</span> {escape(_beneficiary_document(beneficiary))}</td></tr>
    <tr><td colspan=\"2\"><span class=\"label\">Endereço:</span> {escape(getattr(beneficiary, "address", "Não informado"))}</td></tr>
    <tr><td><span class=\"label\">Bairro:</span> {escape(getattr(beneficiary, "neighborhood", "Não informado"))}</td><td><span class=\"label\">Cidade/UF:</span> {escape(getattr(beneficiary, "city_state", "Não informado"))}</td></tr>
    <tr><td><span class=\"label\">CEP:</span> {escape(getattr(beneficiary, "zip_code", "Não informado"))}</td><td><span class=\"label\">Percentual de Participação:</span> {escape(_beneficiary_share(beneficiary))}%</td></tr>
  </table>
"""
                )

            beneficiary_section = f"""
  <div class=\"line\"></div>
  <div class=\"section-title\">{section_title}</div>
  {''.join(rendered_beneficiaries)}
"""
        else:
            beneficiary_section = f"""
  <div class=\"line\"></div>
  <div class=\"section-title\">Dados do Beneficiário</div>
  <table class=\"kv-grid\">
    <tr><td colspan=\"2\"><span class=\"label\">Nome/Razão Social:</span> {escape(data.beneficiary_name)}</td></tr>
    <tr><td colspan=\"2\"><span class=\"label\">Nome Social:</span> {escape(_social_name_or_dash(getattr(data, "beneficiary_social_name", None)))}</td></tr>
    <tr><td colspan=\"2\"><span class=\"label\">CPF/CNPJ:</span> {escape(data.beneficiary_document)}</td></tr>
    <tr><td colspan=\"2\"><span class=\"label\">Endereço:</span> {escape(str(getattr(data, "beneficiary_address", "Não informado") or "Não informado"))}</td></tr>
    <tr><td><span class=\"label\">Bairro:</span> {escape(str(getattr(data, "beneficiary_neighborhood", "Não informado") or "Não informado"))}</td><td><span class=\"label\">Cidade/UF:</span> {escape(str(getattr(data, "beneficiary_city_state", "Não informado") or "Não informado"))}</td></tr>
    <tr><td><span class=\"label\">CEP:</span> {escape(str(getattr(data, "beneficiary_zip_code", "Não informado") or "Não informado"))}</td><td><span class=\"label\">Percentual de Participação:</span> {escape(data.beneficiary_share)}</td></tr>
  </table>
"""

    return f"""
<div class=\"page\">
  {_build_header(data, logo_uri, header_uri, page_number, total_pages)}

  <div class=\"section-box\">
    <span class=\"label\">VIGÊNCIA DO SEGURO:</span> {escape(data.validity_period)}
  </div>

  <div class=\"section-title\">Dados do Segurado</div>
  <table class=\"kv-grid\">
    <tr><td colspan="2"><span class="label">Nome/Razão Social:</span> {escape(data.insured_name)}</td></tr>
    <tr><td colspan="2"><span class="label">Nome Social:</span> {escape(_social_name_or_dash(data.insured_social_name))}</td></tr>
    <tr><td><span class="label">CPF/CNPJ:</span> {escape(data.insured_document)}</td><td><span class="label">Data de Nascimento:</span> {escape(data.insured_birth_date)}</td></tr>
    <tr><td><span class="label">E-mail:</span> {escape(data.insured_email)}</td><td><span class="label">Documento:</span> {escape(data.insured_additional_document)}</td></tr>
    <tr><td><span class="label">Órgão Expedição:</span> {escape(data.insured_document_issuing_authority)}</td><td><span class="label">Data Expedição:</span> {escape(data.insured_document_issue_date)}</td></tr>
    <tr><td colspan="2"><span class="label">Endereço:</span> {escape(data.insured_address)}</td></tr>
    <tr><td><span class="label">Bairro:</span> {escape(data.insured_neighborhood)}</td><td><span class="label">Cidade/UF:</span> {escape(data.insured_city_state)}</td></tr>
    <tr><td><span class="label">CEP:</span> {escape(data.insured_zip_code)}</td><td><span class="label">Telefone(s):</span> {escape(data.insured_phone)}</td></tr>
  </table>

  <div class=\"line\"></div>
  <div class=\"section-title\">Dados da Propriedade</div>
  <table class=\"kv-grid\">
    <tr><td colspan="2"><span class="label">Endereço:</span> {escape(data.property_address)}</td></tr>
    <tr><td><span class="label">Bairro:</span> {escape(data.property_neighborhood)}</td><td><span class="label">Cidade/UF:</span> {escape(data.property_city_state)}</td></tr>
    <tr><td><span class="label">CEP:</span> {escape(data.property_zip_code)}</td><td><span class="label">Código BACEN:</span> {escape(data.property_bacen_code)}</td></tr>
    <tr><td colspan="2"><span class="label">Nome da Propriedade:</span> {escape(data.property_name)}</td></tr>
    <tr><td colspan=\"2\"><span class=\"label\">Coordenadas Geográficas:</span> {escape(data.property_coordinates)}</td></tr>
  </table>

  {beneficiary_section}

  <div class="line"></div>
  {_build_footer(footer_uri)}
</div>
"""


def _build_page_two(
    data: PolicyDocumentData,
    logo_uri: str,
    header_uri: str,
    footer_uri: str,
    page_number: int,
    total_pages: int,
) -> str:
    coverage_rows = "".join(
        (
            "<tr>"
      f"<td>{escape(_row_cell(line, 0))}</td>"
      f"<td>{escape(_row_cell(line, 1))}</td>"
      f"<td>{escape(_row_cell(line, 2))}</td>"
      f"<td>{escape(_row_cell(line, 3))}</td>"
      f"<td>{escape(_row_cell(line, 4))}</td>"
            "</tr>"
        )
        for line in data.coverage_lines
    )

    installment_rows = "".join(
        (
            "<tr>"
        f"<td>{escape(_row_cell(line, 0))}</td>"
        f"<td>{escape(_row_cell(line, 1))}</td>"
        f"<td>{escape(_row_cell(line, 2))}</td>"
        f"<td>{escape(_row_cell(line, 3))}</td>"
        f"<td>{escape(_row_cell(line, 4))}</td>"
            "</tr>"
        )
        for line in data.installments
    )

    return f"""
<div class=\"page\">
  {_build_header(data, logo_uri, header_uri, page_number, total_pages)}

  <div class=\"section-title\">Dados da Corretora de Seguros</div>
  <table class=\"kv-grid\">
    <tr><td colspan=\"2\"><span class=\"label\">Razão Social:</span> {escape(data.broker_name)}</td></tr>
    <tr><td><span class=\"label\">CNPJ:</span> {escape(data.broker_document)}</td><td><span class=\"label\">SUSEP:</span> {escape(data.broker_susep_code)}</td></tr>
    <tr><td colspan=\"2\"><span class=\"label\">Endereço:</span> {escape(data.broker_address)}</td></tr>
    <tr><td><span class=\"label\">Bairro:</span> {escape(data.broker_neighborhood)}</td><td><span class=\"label\">Cidade/UF:</span> {escape(_format_city_state(data.broker_city_state))}</td></tr>
    <tr><td><span class=\"label\">CEP:</span> {escape(data.broker_zip_code)}</td><td><span class=\"label\">Telefone:</span> {escape(data.broker_phone)}</td></tr>
  </table>

  <div class=\"line\"></div>
  <div class=\"section-title\">Dados do Seguro</div>
  <table class=\"kv-grid\">
    <tr><td><span class=\"label\">Cultura:</span> {escape(data.crop)}</td><td><span class=\"label\">Código Bacen:</span> {escape(data.bacen_code)}</td></tr>
    <tr><td><span class=\"label\">Área Total da Cultura:</span> {escape(data.total_area)}ha</td><td><span class=\"label\">Itens Segurados:</span> {escape(data.insured_items)}</td></tr>
    <tr><td><span class=\"label\">LMGA:</span> {escape(data.lmga)}</td><td><span class=\"label\">Prêmio Total:</span> {escape(data.total_premium)}</td></tr>
  </table>

  <div class=\"line\"></div>
  <div class=\"section-title\">Demonstrativo das Coberturas Contratadas</div>
  <table class=\"table coverage-table\">
    <thead>
      <tr>
        <th>Coberturas</th>
        <th>Tipo</th>
        <th>Franquia</th>
        <th>LMI</th>
        <th>Prêmio</th>
      </tr>
    </thead>
    <tbody>
      {coverage_rows}
    </tbody>
  </table>

  <div class=\"premium-summary\">
    <div class=\"premium-summary-line mono-strong\">Prêmio Líquido - {escape(data.policy_net_premium)}</div>
    <div class=\"premium-summary-line mono-strong\">Custo de Apólice - {escape(data.policy_cost)}</div>
    <div class=\"premium-summary-line mono-strong\">IOF - {escape(data.iof)}</div>
    <div class="premium-summary-line mono-strong">Prêmio a Pagar - {escape(data.policy_net_premium)}</div>
  </div>

  <div class=\"section-title\">Forma de Pagamento</div>
  <table class=\"table installment-table\">
    <thead>
      <tr>
        <th>Nº da<br/>Parcela</th>
        <th>Vencimento</th>
        <th>Prêmio Total<br/>da Parcela</th>
        <th>Nº Documento</th>
        <th>Pagador</th>
      </tr>
    </thead>
    <tbody>
      {installment_rows}
    </tbody>
  </table>

  {_build_footer(footer_uri)}
</div>
"""


def _build_page_risk(
    data: PolicyDocumentData,
    logo_uri: str,
    header_uri: str,
    footer_uri: str,
    page_number: int,
    total_pages: int,
    items: list[list[str]],
) -> str:
    if not items:
        return ""

    rendered_items = []
    for item in items:
        rendered_items.append(
            f"""
<div style=\"margin-bottom: 7px;\">
  <div class=\"mono-strong\">Item: {escape(_row_cell(item, 0))}</div>
  <table class=\"kv-grid\">
    <tr><td><span class=\"label\">Quadra/Talhão:</span> {escape(_row_cell(item, 1))}</td><td><span class=\"label\">Variedade:</span> {escape(_row_cell(item, 4))}</td></tr>
    <tr><td><span class=\"label\">Área (ha):</span> {escape(_row_cell(item, 2))}</td><td><span class=\"label\">PE (ton/ha):</span> {escape(_row_cell(item, 5))}</td></tr>
    <tr><td><span class=\"label\">Valor (R$/ton):</span> {escape(_row_cell(item, 3))}</td><td><span class=\"label\">LMG:</span> {escape(_row_cell(item, 6))}</td></tr>
    <tr><td colspan=\"2\"><span class=\"label\">Coordenadas Geográficas:</span> {escape(_row_cell(item, 7))}</td></tr>
  </table>

  <table class=\"table\">
    <thead>
      <tr>
        <th>Cobertura</th>
        <th>Franquia (R$)</th>
        <th>LMI</th>
        <th>Prêmio Líquido</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>{escape(data.main_coverage)}</td>
        <td>{escape(_row_cell(item, 10))}</td>
        <td>{escape(_row_cell(item, 9))}</td>
        <td>{escape(_row_cell(item, 11))}</td>
      </tr>
    </tbody>
  </table>
</div>
"""
        )

    body = "".join(rendered_items)

    return f"""
<div class=\"page\">
  {_build_header(data, logo_uri, header_uri, page_number, total_pages)}
  <div class=\"section-title\">Descrição do Risco e Coberturas Contratadas</div>
  <div class=\"line\"></div>
  {body}
  {_build_footer(footer_uri)}
</div>
"""


def _build_legal_pages(
    data: PolicyDocumentData,
    logo_uri: str,
    header_uri: str,
    footer_uri: str,
    legal_contents: list[str],
    start_page_number: int,
    total_pages: int,
) -> list[str]:
    pages: list[str] = []
    page_number = start_page_number
    for content in legal_contents:
        pages.append(
            f"""
<div class=\"page\">
  {_build_header(data, logo_uri, header_uri, page_number, total_pages)}
  {content}
  {_build_footer(footer_uri)}
</div>
"""
        )
        page_number += 1

    return pages


def _build_legal_page_contents(data: PolicyDocumentData, signature_uri: str) -> list[str]:
    signature_markup = (
        f"<img class=\"signature-image\" src=\"{escape(signature_uri)}\" alt=\"Assinatura Diretora\" />"
        if signature_uri
        else "<div class=\"signature-name\">Vanessa Arteaga</div>"
    )
    signature_issue_date = _format_date_with_full_month_name(data.issue_date)

    return [
        """
<div class=\"section-title\">Informações Importantes para o Segurado</div>
<div class=\"text-block\">
  <p>Leia atentamente as Condições Gerais, Especiais e Particulares, principalmente as exclusões.</p>
  <p>Veja a relação de RISCOS E BENS EXCLUÍDOS do produto SEGURO AGRÍCOLA FRUTAS E HORTALIÇAS contantes do ANEXO I desta apólice de seguros. Confira os dados constantes nesta apólice e, em caso de divergências, procure imediatamente seu Corretor.</p>
  <p>Confira os dados constantes nesta apólice e, em caso de divergências, procure imediatamente seu Corretor.</p>
  <p>Quaisquer modificações à presente apólice deverão ser feitas através do seu Corretor à Seguradora de forma expressa e só serão válidas após anuência da Seguradora.</p>
  <p>Este seguro é por prazo determinado tendo a seguradora a faculdade de não renovar a apólice na data de vencimento, sem devolução dos prêmios pagos nos termos da apólice.</p>
  <p>Limites Máximos de Indenização e Limites Máximos de Garanta não sujeitos à atualização monetária.</p>
  <p>As Condições Gerais, Especiais e Particulares deste seguro estão disponíveis no SITE da SEGURADORA – www.essor.com.br - e, a qualquer tempo, sua versão física poderá ser fornecida mediante solicitação à Seguradora.</p>
  <p>O Segurado poderá consultar a situação cadastral de seu Corretor de Seguros no site www.susep.gov.br, por meio do número de seu registro na SUSEP, nome completo, CNPJ ou CPF.</p>
  <p>As condições contratuais/regulamentos desse produto protocolizados pela Seguradora junto à SUSEP poderão ser consultados no endereço eletrônico www.susep.gov.br, de acordo com o número de processo constante da apólice.</p>
  <p>Processo SUSEP nº {process}.</p>
  <p>O registro deste plano na SUSEP não implica, por parte da autarquia, incentivo ou recomendação a sua comercialização.</p>
  <p>SUSEP – Superintendência de Seguros Privados – Autarquia Federal responsável pela fiscalização, normatização e controle dos mercados de seguro, previdência complementar aberta, capitalização, resseguro e corretagem de seguros.</p>
  <p>Atendimento gratuito SUSEP 0800 021 8484.</p>
  <p>Em atendimento à Lei 12.741/12 informamos que incidem as alíquotas de 0,65% de PIS/PASEP e de 4% de COFINS sobre os prêmios de seguros, deduzidos do estabelecido em legislação específica.</p>
  <p>O Grupo SCOR, controlador da ESSOR, é membro do Pacto Global das Nações</p>
  </div>
""".format(process=escape(data.susep_process)),
"""
  <p> Unidas, em razão do que possui o compromisso de respeitar os direitos humanos na condução de suas atividades comerciais; repudia a violação, ou potencial violação, dos direitos humanos; e não apoia, nem tolera qualquer forma de abuso humano, servidão, trabalho forçado, trabalho compulsório, tráfico humano ou escravidão em suas empresas e tampouco em qualquer empresa com a qual esteja envolvida em uma transação comercial, conforme disposto no seu Código de Conduta, acessível no site https://essor.com.br/. Neste sentido, o proponente, por si, seus sócios, diretores, empregados, agentes prepostos, e outras pessoas que venham a agir em seu nome, direta e indiretamente, declarou na proposta de seguro que tem conhecimento do Código de Conduta da Essor e que se absterá da prática de violações aos direitos humanos, bem como cumprirá quaisquer legislação, regulamentações e normativos aplicáveis à proteção e respeito a estes direitos na condução de suas atividades, sob pena de cancelamento da apólice e perda de direito à indenização nos termos das condições deste contrato de seguro. </p>
  <p>Caso haja subvenção ao prêmio pelo Governo Federal, a mesma fica condicionada à regularidade do Segurado junto ao CADIN, conforme Termo de Responsabilidade do Produtor Rural firmado pelo Segurado, bem como a existência de recursos pelo Ministério da Agricultura, na forma da Resolução 13 do Comitê Gestor Interministerial do Seguro Rural (CGSR). Não estando o Segurado regularizado junto ao CADIN, ou inexistindo recursos do Ministério da Agricultura para subvencionar o prêmio, ou ainda, se não se enquadrar nas normas reguladoras da matéria, o Segurado será obrigado a custear 100% do prêmio com recursos próprios.</p>
  <p>Para melhor atendê-los, a ESSOR oferece dois canais de atendimento: o Serviço de Atendimento ao Cliente (SAC) e a Ouvidoria. Recomendamos que, inicialmente, entre em contato com o SAC para resolver suas questões. Caso o SAC não consiga atender satisfatoriamente sua situação, você pode acionar a Ouvidoria para uma análise mais detalhada e imparcial.</p>
  <ul>
    <li>SAC: 0800 521 1007 - E-mail: faleconosco@essor.com.br</li>
    <li>Ouvidoria: 0800 777 0438 - E-mail: ouvidoria@essor.com.br</li>
    <li>Atendimento ao deficiente auditivo e de fala: consultar site www.essor.com.br</li>
  </ul>
  <p> </p>
  <p>Plataforma oficial para registro de reclamação dos consumidores dos mercados supervisionados: www.consumidor.gov.br</p>
  
  </div>
""",
        """
<div class=\"section-title\" style=\"font-weight: 700;\">Anexo I</div>
<div class=\"text-block\" style=\"font-weight: 700;\">
  <p>Conforme CLÁUSULA 5ª - RISCOS EXCLUÍDOS das Condições Gerais do Seguro:</p>
  <p>5.1. EXCLUSÃO DE COBERTURA PARA VÍCIOS OCULTOS</p>
  <p>5.1.1. FICA EXCLUÍDA DA COBERTURA DESTE SEGURO QUALQUER INDENIZAÇÃO DECORRENTE DE VÍCIOS OCULTOS NÃO DECLARADOS, CONFORME DEFINIÇÃO LEGAL E CONTRATUAL.</p>
  <p>5.1.2. PARA FINS DESTA CLÁUSULA, CONSIDERA-SE VÍCIO OCULTO O DEFEITO PREEXISTENTE À VIGÊNCIA DO SEGURO, NÃO APARENTE E NÃO DECLARADO PELO SEGURADO, QUE COMPROMETA A INTEGRIDADE, FUNCIONAMENTO OU VALOR DO BEM SEGURADO.</p>
  <p>5.1.3. A OMISSÃO, DOLOSA OU CULPOSA, DE INFORMAÇÕES RELEVANTES SOBRE O ESTADO DO BEM, OU A PRESTAÇÃO DE INFORMAÇÕES INVERÍDICAS PELO SEGURADO, EXCLUI A COBERTURA PARA VÍCIOS OCULTOS NÃO DECLARADOS NO MOMENTO DA CONTRATAÇÃO, SEM PREJUÍZO DAS DEMAIS CONSEQUÊNCIAS LEGAIS E CONTRATUAIS.</p>
  <p>5.1.4. A EXCLUSÃO PREVISTA NESTA CLÁUSULA NÃO SE APLICA:</p>
  <p>A) AOS VÍCIOS OCULTOS DEVIDAMENTE DECLARADOS PELO SEGURADO NO MOMENTO DA CONTRATAÇÃO; E</p>
  <p>B) AOS VÍCIOS QUE, COMPROVADAMENTE, NÃO PODERIAM SER IDENTIFICADOS PELO SEGURADO, MESMO COM A DEVIDA DILIGÊNCIA, SALVO SE A SEGURADORA, AO TEMPO DACONTRATAÇÃO, TINHA CONHECIMENTO DO VÍCIO OU DEIXOU DE ADOTAR PROVIDÊNCIAS PARA SUA IDENTIFICAÇÃO.</p>
  <p>5.1.5. O SEGURADO DEVERÁ DECLARAR EXPRESSAMENTE O ESTADO DO BEM NO MOMENTO DA CONTRATAÇÃO.</p>
  <p> </p>
  <p>5.2. ATOS DOLOSOS, ILÍCITOS E RESPONSABILIDADE</p>
  <p>5.2.1. NÃO HAVERÁ COBERTURA DO SEGURO PARA:</p>
  <p>A) MULTAS E OUTRAS PENALIDADES APLICADAS EM VIRTUDE DE ATOS COMETIDOS PESSOALMENTE PELO SEGURADO QUE CARACTERIZEM ILÍCITO CRIMINAL, NOS TERMOS DO ART. 10, PARÁGRAFO ÚNICO, INCISO I, DA LEI 15.040/2024;</p>
  <p>B) ATOS DOLOSOS (INTENCIONAIS) OU PRATICADOS COM CULPA GRAVE EQUIPARÁVEL AO DOLO PELO SEGURADO, PELO BENEFICIÁRIO OU POR SEUS REPRESENTANTES LEGAIS, EXCETO NOS CASOS EM QUE O DOLO SEJA PRATICADO EXCLUSIVAMENTE PELO REPRESENTANTE EM PREJUÍZO DO SEGURADO OU BENEFICIÁRIO (LEI 15.040/2024, ART. 10, PARÁGRAFO ÚNICO, II);</p>
  <p>SE O SEGURADO FOR PESSOA JURÍDICA, ESTA EXCLUSÃO SE APLICA TAMBÉM AOS SÓCIOS CONTROLADORES, DIRIGENTES, ADMINISTRADORES, BENEFICIÁRIOS E REPRESENTANTES DE CADA UMA DESSAS PESSOAS.</p>
  <p>5.2.2. A ELIMINAÇÃO OU DESTRUIÇÃO INTENCIONAL OU CONFISCO DO BEM SEGURADO, QUANDO SEJA ORDENADA OU EFETUADA PELA AUTORIDADE COMPETENTE QUE TENHA JURISDIÇÃO SOBRE A MATÉRIA.</p>
</div>
""",
"""
<div class=\"text-block\" style=\"font-weight: 700;\">
  <p>5.2.3. ATOS DE AUTORIDADES PÚBLICAS, SALVO SE PARA EVITAR PROPAGAÇÃO DOS RISCOS COBERTOS POR ESTA APÓLICE OU CERTIFICADO DE SEGURO.</p>
  <p> </p>
  <p>5.3. RISCOS TÉCNICOS E OPERACIONAIS</p>
  <p>5.3.1. RISCO IMPOSSÍVEL OU QUE JÁ TENHA SE REALIZADO;</p>
  <p>5.3.2. DESPESAS COM PREVENÇÃO ORDINÁRIA, CONSIDERADA COMO QUALQUER ESPÉCIE DE MANUTENÇÃO OU MEDIDAS PREVENTIVAS ROTINEIRAS, POR NÃO CARACTERIZAREM DESPESAS DE SALVAMENTO;</p>
  <p>5.3.3. DESPESAS COM MEDIDAS NOTORIAMENTE INADEQUADAS, CONSIDERADAS COMO AQUELAS QUE NÃO SÃO APROPRIADAS OU EFICAZES PARA CONTER OU SALVAR OS BENS EM RISCO DURANTE UM SINISTRO;</p>
  <p>5.3.4. MEDIDAS QUE NÃO SEGUEM AS RECOMENDAÇÕES DA SEGURADORA;</p>
  <p>5.3.5. MEDIDAS EXCESSIVAS OU DESNECESSÁRIAS, CONSIDERADAS COMO SENDO AQUELAS QUE VÃO ALÉM DO NECESSÁRIO PARA CONTER O SINISTRO OU QUE SÃO DESPROPORCIONAIS AO RISCO ENVOLVIDO; E</p>
  <p>5.3.6. DESPESAS EXCEDENTES AO LIMITE ESPECIFICADO NA APÓLICE, OU NA FALTA DESTE, SUPERIOR A 20% DO LIMITE MÁXIMO DE INDENIZAÇÃO OU CAPITAL GARANTIDO APLICÁVEL AO TIPO DE SINISTRO.</p>
  <p> </p>
  <p>5.4. EXCLUSÕES POR EVENTOS AMBIENTAIS E POR NÃO-CONFORMIDADE AMBIENTAL, SOCIAL E CLIMÁTICA</p>
  <p>5.4.1. RISCOS AMBIENTAIS E NATURAIS</p>
  <p>5.4.1. 1. DEFINIÇÃO: TRATA DE EVENTOS FÍSICOS E EXTERNOS QUE PODEM CAUSAR DANOS AO BEM SEGURADO, COMO:</p>
  <ul>
    <li>FENÔMENOS NATURAIS (INUNDAÇÃO, TERREMOTO, ERUPÇÃO VULCÂNICA).</li>
    <li>EVENTOS EXTREMOS DE ORIGEM HUMANA OU BÉLICA (GUERRA, TERRORISMO).</li>
    <li>POLUIÇÃO, CONTAMINAÇÃO, RADIAÇÃO.</li>
  </ul>
  <p>5.4.1.2. EXCLUSÕES DA COBERTURA:</p>
  <p>A) INUNDAÇÃO, SALVO SE CAUSADA POR EVENTO COBERTO CONFORME DEFINIDO NAS CONDIÇÕES ESPECIAIS DA COBERTURA CONTRATADA;</p>
  <p>B) PERDAS CAUSADAS POR CATACLISMOS TAIS COMO TERREMOTOS E ERUPÇÕES VULCÂNICAS;</p>
  <p>C) PERDAS QUE, DIRETA OU INDIRETAMENTE, FOREM ORIGINADAS EM CONSEQUÊNCIA DE GUERRA, INVASÃO, ATOS DE INIMIGOS ESTRANGEIROS; HOSTILIDADES E OPERAÇÕES BÉLICAS, COM OU SEM DECLARAÇÃO DE GUERRA, GUERRA CIVIL, REBELIÃO, REVOLUÇÃO, INSURREIÇÃO, REVOLTAS, MOTINS OU ATOS QUE AS LEIS CLASSIFICAM COMO DELITOS CONTRA A SEGURANÇA INTERNA DO ESTADO;</p>
  <p>D) NÃO ESTARÃO COBERTOS DANOS E PERDAS CAUSADOS DIRETA OU INDIRETAMENTE POR ATO TERRORISTA, CABENDO À SEGURADORA COMPROVAR COM DOCUMENTAÇÃO HÁBIL,</p>
</div>
""",
"""
<div class=\"text-block\" style=\"font-weight: 700;\">
  <p>ACOMPANHADA DE LAUDO CIRCUNSTANCIADO QUE CARACTERIZE A NATUREZA DO ATENTADO, INDEPENDENTEMENTE DE SEU PROPÓSITO, E DESDE QUE ESTE TENHA SIDO DEVIDAMENTE RECONHECIDO COMO ATENTATÓRIO À ORDEM PÚBLICA PELA AUTORIDADE PÚBLICA COMPETENTE;</p>
  <p>E) PERDAS CAUSADAS OU RESULTANTES DE QUALQUER TIPO DE POLUIÇÃO OU CONTAMINAÇÃO, SEJAM SÚBITAS OU GRADUAIS;</p>
  <p>F) PERDAS PROVENIENTES DIRETA OU INDIRETAMENTE DE REAÇÃO NUCLEAR, RADIAÇÃO NUCLEAR OU CONTAMINAÇÃO RADIOATIVA, QUALQUER QUE SEJA A ORIGEM QUE AS CAUSEM; E</p>
  <p>G) PERDAS OCASIONADAS POR ONDAS SÔNICAS CAUSADAS POR AVIÕES OU OUTRAS AERONAVES QUE VOEM A VELOCIDADE SÔNICA OU SUPERSÔNICA.</p>
  <p>5.4.2. RISCOS RELATIVOS À CONFORMIDADE AMBIENTAL, SOCIAL E CLIMÁTICA</p>
  <p>5.4.2.1. DEFINIÇÃO: RISCOS INERENTES À IRREGULARIDADE DA ATIVIDADE SEGURADA (NÃO CONFORMIDADE AMBIENTAL/SOCIAL);</p>
  <p>5.4.2.2. FICAM EXPRESSAMENTE EXCLUÍDOS DA COBERTURA DESTE SEGURO OS EVENTOS, DANOS, PERDAS OU PREJUÍZOS RELACIONADOS, DIRETA OU INDIRETAMENTE, A BENS, PROPRIEDADES RURAIS OU ATIVIDADES AGROPECUÁRIAS QUE NÃO OBSERVEM AS DISPOSIÇÕES DOS ARTS. 3º E 4º DA RESOLUÇÃO CNSP Nº 485/2025, BEM COMO AS DEMAIS NORMAS AMBIENTAIS, SOCIAIS E CLIMÁTICAS VIGENTES;</p>
  <p> </p>
  <p>5.4.2.3. SEM PREJUÍZO DAS DEMAIS EXCLUSÕES PREVISTAS NESTAS CONDIÇÕES GERAIS, NÃO ESTARÃO COBERTOS OS RISCOS VINCULADOS A:</p>
  <p>A) QUAISQUER BENS OU ATIVIDADES RURAIS LOCALIZADOS EM IMÓVEL RURAL QUE NÃO POSSUA INSCRIÇÃO VÁLIDA NO CADASTRO AMBIENTAL RURAL (CAR), OU CUJA INSCRIÇÃO SE ENCONTRE SUSPENSA, CANCELADA OU INATIVA;</p>
  <p>B) QUAISQUER BENS OU ATIVIDADES RURAIS SITUADAS EM IMÓVEL TOTAL OU PARCIALMENTE INSERIDO EM UNIDADE DE CONSERVAÇÃO DE DOMÍNIO PÚBLICO EXCLUSIVO, SALVO QUANDO A ATIVIDADE SEGURADA ESTEJA EXPRESSAMENTE PREVISTA NO RESPECTIVO PLANO DE MANEJO OU AUTORIZADA PELO ÓRGÃO GESTOR;</p>
  <p>C) QUAISQUER BENS OU ATIVIDADES RURAIS SITUADAS EM IMÓVEL TOTAL OU PARCIALMENTE INSERIDO EM TERRA INDÍGENA HOMOLOGADA, TERRA DE QUILOMBO OU ÁREA DE COMUNIDADE REMANESCENTE OU TRADICIONAL, NOS TERMOS DA LEGISLAÇÃO VIGENTE, EXCETO QUANDO O SEGURADO INTEGRE A PRÓPRIA COMUNIDADE BENEFICIÁRIA OU POSSUA AUTORIZAÇÃO LEGAL PARA A ATIVIDADE;</p>
  <p>D) QUAISQUER BENS OU ATIVIDADES RURAIS SITUADAS EM IMÓVEL SITUADO EM FLORESTA PÚBLICA TIPO B NÃO DESTINADA, REGISTRADA NO CADASTRO NACIONAL DE FLORESTAS PÚBLICAS DO SERVIÇO FLORESTAL BRASILEIRO, SALVO NAS HIPÓTESES EXPRESSAMENTE ADMITIDAS NA LEGISLAÇÃO VIGENTE;</p>
</div>
""",
"""
<div class=\"text-block\" style=\"font-weight: 700;\">
  <p>E) SEGURADO, PESSOA FÍSICA OU JURÍDICA, INSCRITO NO CADASTRO DE EMPREGADORES QUE TENHAM SUBMETIDO TRABALHADORES A CONDIÇÕES ANÁLOGAS À DE ESCRAVO, INSTITUÍDO E ADMINISTRADO PELO PODER EXECUTIVO FEDERAL, INDEPENDENTEMENTE DO BEM OU ATIVIDADE RURAL PARA A QUAL ESTEJA SENDO SOLICITADA A CONTRATAÇÃO DO SEGURO;</p>
  <p>F) BENS OU ATIVIDADES RURAIS REALIZADAS EM IMÓVEL RURAL EMBARGADO POR AUTORIDADE AMBIENTAL ESTADUAL OU FEDERAL — INCLUSIVE REGISTRADO NO CADASTRO DE EMBARGOS AMBIENTAIS DO IBAMA — DECORRENTE DE USO ECONÔMICO DE ÁREAS DESMATADAS ILEGALMENTE, SALVO QUANDO COMPROVADO QUE:</p>
  <p>I. AS MULTAS AMBIENTAIS FORAM PAGAS OU HÁ PROVA DE TER SIDO INICIADA A RECUPERAÇÃO DA ÁREA DEGRADADA; E</p>
  <p>II. O IMÓVEL POSSUI CAR ATIVO E A ÁREA EMBARGADA CORRESPONDE A NO MÁXIMO 5% (CINCO POR CENTO) DA ÁREA TOTAL OU 20 (VINTE) HECTARES, O QUE FOR MENOR;</p>
  <p>G) ÁREAS OU ATIVIDADES EM PROCESSO DE REGULARIZAÇÃO AMBIENTAL QUE NÃO TENHAM SIDO FORMALMENTE APROVADAS PELOS ÓRGÃOS COMPETENTES NO MOMENTO DA CONTRATAÇÃO DO SEGURO; E</p>
  <p>H) QUALQUER OUTRO RISCO QUE INFRINJA AS CONDIÇÕES AMBIENTAIS, SOCIAIS OU DE GOVERNANÇA (ASG) DEFINIDAS EM NORMAS REGULATÓRIAS OU EM PROGRAMAS DE SUBVENÇÃO FEDERAL VINCULADOS AO SEGURO RURAL.</p>
  <p> </p>
  <p>5.4.2.4. A SEGURADORA PODERÁ SOLICITAR, A QUALQUER TEMPO, DOCUMENTAÇÃO COMPROBATÓRIA DA REGULARIDADE AMBIENTAL E SOCIAL DO IMÓVEL OU ATIVIDADE SEGURADA, INCLUINDO A CERTIDÃO DE REGULARIDADE DO CAR, DECLARAÇÕES DO IBAMA, CERTIDÕES DE NÃO EMBARGO, COMPROVAÇÃO DE ADESÃO A PROGRAMAS DE RECUPERAÇÃO AMBIENTAL E OUTROS DOCUMENTOS EXIGIDOS PELA LEGISLAÇÃO VIGENTE; E</p>
  <p>5.4.2.5. A SEGURADORA OBSERVA NO MOMENTO DA CONTRATAÇÃO AS DIRETRIZES AMBIENTAIS, SOCIAIS E CLIMÁTICAS PREVISTAS NA RESOLUÇÃO CNSP 485/2025, EM RAZÃO DISSO, A VERIFICAÇÃO, A QUALQUER TEMPO, DE QUALQUER DAS SITUAÇÕES PREVISTAS NA CLÁUSULA 5.4.2.2 PODERÁ IMPLICAR A RECUSA DA PROPOSTA, A RESOLUÇÃO DO CONTRATO, A REDUÇÃO PROPORCIONAL DA INDENIZAÇÃO OU A PERDA TOTAL DE DIREITO À INDENIZAÇÃO, CONFORME O CASO, E NOS TERMOS DAS DEMAIS DISPOSIÇÕES CONTRATUAIS.</p>
  <p>5.4.2.6. A VERIFICAÇÃO, A QUALQUER TEMPO, DE QUALQUER DAS SITUAÇÕES PREVISTAS NESTA CLÁUSULA PODERÁ IMPLICAR A RECUSA DA PROPOSTA, A RESOLUÇÃO DO CONTRATO, A REDUÇÃO PROPORCIONAL DA INDENIZAÇÃO OU A PERDA TOTAL DE DIREITO À INDENIZAÇÃO, CONFORME O CASO E NOS TERMOS DAS DEMAIS DISPOSIÇÕES CONTRATUAIS.</p>
  <p> </p>
  <p>5.5. RISCOS RELACIONADOS À PRODUÇÃO AGRÍCOLA</p>
</div>
""",
"""
<div class=\"text-block\" style=\"font-weight: 700;\">
  <p>5.5.1. AS PERDAS NORMAIS E/OU PRÓPRIAS DO PROCESSO BIOLÓGICO DE GERMINAÇÃO DA SEMENTE E DO DESENVOLVIMENTO DA CULTURA SEGURADA;</p>
  <p>5.5.2. AS PERDAS E DANOS DE QUALQUER NATUREZA, QUE TENHAM AFETADO A CULTURA SEGURADA ANTES DO INÍCIO OU APÓS O FINAL DE VIGÊNCIA DA PRESENTE APÓLICE OU DO CERTIFICADO DE SEGURO;</p>
  <p>5.5.3. AS PERDAS OCASIONADAS POR ENFERMIDADES, ERVAS DANINHAS OU PRAGAS DE QUALQUER TIPO OU ORIGEM, AINDA QUE UTILIZADOS MÉTODOS VIÁVEIS E EXISTENTES PARA SEU CONTROLE;</p>
  <p>5.5.4. CULTURAS DESTINADAS PARA EXPERIMENTAÇÃO OU AS PERDAS CAUSADAS POR EXPERIMENTOS E/OU ENSAIOS DE QUALQUER NATUREZA;</p>
  <p>5.5.5. AS PERDAS CAUSADAS POR APLICAÇÃO DELIBERADA OU INVOLUNTÁRIA DE PRODUTOS QUÍMICOS NÃO ESPECÍFICOS, NÃO REGISTRADOS OU NÃO RECOMENDADOS EM QUANTIDADE OU QUALIDADE PARA A PROTEÇÃO DA CULTURA SEGURADA;</p>
  <p>5.5.6. AS PERDAS CAUSADAS POR APLICAÇÃO DELIBERADA OU INVOLUNTÁRIA DE PRODUTOS QUÍMICOS ESPECÍFICOS, REGISTRADOS PARA A PROTEÇÃO DA CULTURA SEGURADA, PORÉM, EM QUANTIDADES NÃO RECOMENDADAS;</p>
  <p>5.5.7. AS PERDAS CAUSADAS POR AÇÃO DIRETA DE INSETOS, AVES, ANIMAIS DOMÉSTICOS OU ANIMAIS SILVESTRES;</p>
  <p> </p>
  <p>5.5.8. AS PERDAS CAUSADAS POR AÇÃO DO CALOR OU FOGO PROVOCADO PELO SEGURADO OU DEPENDENTES;</p>
  <p>5.5.9. AS PERDAS OU DANOS CAUSADOS POR ROUBO OU FURTO DO BEM SEGURADO;</p>
  <p>5.5.10. AS PERDAS DE RECEITA DE TODO TIPO, RESULTANTES DA SUSPENSÃO PERMANENTE OU TEMPORÁRIA DA OPERAÇÃO DE PRODUÇÃO AGRÍCOLA, AINDA QUE A CAUSA MATERIAL DESTA TENHA SIDO INDENIZADA; ASSIM COMO OBRIGAÇÕES CONTRATUAIS DO SEGURADO, LUCRO CESSANTE E/OU PREJUÍZOS POR PARALISAÇÃO DAS ATIVIDADES;</p>
  <p>5.5.11. A CULTURA FOR CONDUZIDA EM DESACORDO COM AS RECOMENDAÇÕES TÉCNICAS OFICIAIS DE PESQUISA E ASSISTÊNCIA, ESPECIALMENTE NO QUE SE REFERE A QUANTIDADE, QUALIDADE, VARIEDADE E SANIDADE DE SEMENTES E/OU MUDAS, BEM COMO A QUANTIDADE E QUALIDADE DO ADUBO DE BASE;</p>
  <p>5.5.12. EVENTOS OCORRIDOS EM CULTURAS IMPLANTADAS EM LOCAL DIFERENTE DO INFORMADO NA PROPOSTA;</p>
  <p>5.5.13. GERMINAÇÃO OU EMERGÊNCIA INADEQUADA: PROVOCADAS POR SEMEADURA DESUNIFORME OU INADEQUADA, FALTA DE UMIDADE NO SOLO NO MOMENTO DO PLANTIO, PROBLEMAS DE SALINIDADE DO SOLO, INUNDAÇÃO, ESCORRIMENTO OU ENCROSTAMENTO SUPERFICIAL, POTENCIALIZADO OU NÃO PELOS RISCOS COBERTOS;</p>
  <p>5.5.14. PERDAS CAUSADAS POR SEMENTES DE MÁ QUALIDADE, QUER SEJA POR BAIXO VIGOR OU BAIXO PODER GERMINATIVO;</p>
</div>
""",
"""
<div class=\"text-block\" style=\"font-weight: 700;\">
  <p>5.5.15. PERDAS POR PROBLEMAS DE SOLO PROVOCADO POR: DEFICIÊNCIA NUTRICIONAL, SALINIDADE, TOXICIDADE DE ALUMÍNIO OU OUTRO COMPONENTE, FUNGOS, NEMATOIDES, DUMPING OFF E COMPACTAÇÃO DO SOLO;</p>
  <p>5.5.16. PERDAS OCASIONADAS POR ATAQUES DE INSETOS, DOENÇAS OU VIROSES;</p>
  <p>5.5.17. PERDAS EM LINHAS DE PLANTIO: PROVOCADAS POR DANOS MECÂNICOS E OU DE MAQUINÁRIO, EXCESSO OU DEFICIÊNCIA DE DEFENSIVOS AGRÍCOLAS APLICADOS, PRÁTICAS DE SEMEADURA OU TRANSPLANTE INADEQUADOS E PRAGAS RADICULARES DISSEMINADAS ATRAVÉS DE TRATOS CULTURAIS;</p>
  <p>5.5.18. PERDAS EM PLANTAS DISPERSAS: PROVOCADAS POR MAQUINÁRIO E OU ANIMAIS, OU MÁ FORMAÇÃO FÍSICA ATRIBUÍDA À VARIAÇÃO GENÉTICA, AGENTES PATÓGENOS EM SEMENTES;</p>
  <p>5.5.19. PERDAS EM BORDADURAS INCLUINDO, MAS NÃO SE LIMITANDO A: DERIVA DE APLICAÇÕES DE DEFENSIVOS AGRÍCOLAS EM CULTURAS VIZINHAS, INUNDAÇÕES, DESNÍVEIS DE TERRENO, PASSAGEM DE ANIMAIS E COMPACTAÇÃO POR MAQUINÁRIO;</p>
  <p> </p>
  <p>5.5.20. OBRIGAÇÕES CONTRATUAIS DO SEGURADO, LUCROS CESSANTES, IMPOSSIBILIDADE DE VENDA DOS PRODUTOS NO MERCADO E/OU PREJUÍZOS POR PARALISAÇÃO DAS ATIVIDADES;</p>
  <p>5.5.21. PERDAS OCORRIDAS EM LAVOURAS COM CULTIVO ORGÂNICO;</p>
  <p>5.5.22. PERDAS OCORRIDAS EM LAVOURAS SEMEADAS “À LANÇO”. ESTA CLÁUSULA NÃO SE APLICA À CULTURA DE ARROZ;</p>
  <p>5.5.23. PERDAS DE QUALQUER NATUREZA SOFRIDAS DURANTE O PERÍODO DE CARÊNCIA DA APÓLICE;</p>
  <p>5.5.24. AS PERDAS DE QUALQUER NATUREZA ANTECEDENTES E/OU POSTERIORES A REALIZAÇÃO E/OU CONCLUSÃO DE PLANTIO QUE DESRESPEITAREM A DATA PACTUADA NA PROPOSTA DE SEGURO, SOBERANA E INDEPENDENTE DO PERÍODO PREVISTO NAS RECOMENDAÇÕES TÉCNICAS DOS ÓRGÃOS OFICIAIS E/OU DO SISTEMA DE ZONEAMENTO AGRÍCOLA DE RISCO CLIMÁTICO (MAPA) PARA A CULTURA SEGURADA; SEM PREJUÍZO DA INCIDÊNCIA DO SUBITEM 24.1 DA CLÁUSULA 24ª - PRAZO DO SEGURO E AVISO DO INÍCIO DA COLHEITA DESTAS CONDIÇÕES GERAIS;</p>
  <p>5.5.25. PERDAS OCORRIDAS EM LAVOURAS DE SOJA, MILHO E ALGODÃO EM CAROÇO IMPLANTADAS COM VARIEDADE CONVENCIONAL (NÃO TRANSGÊNICA) NOS ESTADOS PERTENCENTES ÀS REGIÕES CENTRO-OESTE, NORDESTE E NORTE; E</p>
  <p>5.5.26. PERDAS OCORRIDAS EM LAVOURAS DE GRÃOS IMPLANTADAS COM SEMENTES QUE SEJAM PROVENIENTES DE FONTES NÃO AUTORIZADAS OU QUE NÃO ATENDAM ÀS NORMAS TÉCNICAS EXIGIDAS PELO MAPA.</p>
  <p> </p>
  <p>5.6. QUESTÕES COMERCIAIS E CONTRATUAIS</p>
</div>
""",
"""
<div class=\"text-block\" style=\"font-weight: 700;\">
  <p>5.6.1. QUEDA DE COTAÇÃO DOS PRODUTOS NO MERCADO;</p>
  <p>5.6.2. IMPOSSIBILIDADE DE VENDA DOS PRODUTOS NO MERCADO; e</p>
  <p>5.6.3. QUALIDADE DO PRODUTO COLHIDO, MESMO QUE EM DECORRÊNCIA DE EVENTO COBERTO.</p>
  <p> </p>
  <p>5.7. RISCOS CIBERNÉTICOS E DIREITOS HUMANOS</p>
  <p>5.7.1. QUALQUER PERDA POR ATAQUE CIBERNÉTICO, DANO, RESPONSABILIDADE, CUSTO OU DESPESA DIRETA OU INDIRETAMENTE CAUSADA POR:</p>
  <p>5.7.1.1. USO OU INCAPACIDADE DE USAR QUALQUER COMPUTADOR, SISTEMA DE COMPUTADOR, PROGRAMA DE SOFTWARE DE COMPUTADOR, PROCESSO COMPUTACIONAL OU QUALQUER OUTRO SISTEMA ELETRÔNICO;</p>
  <p>5.7.1.2. QUALQUER VÍRUS DE COMPUTADOR OU CÓDIGO MALICIOSO; E</p>
  <p>5.7.1.3. QUALQUER FRAUDE REFERENTE A COMPUTADOR QUE ESTEJA RELACIONADA AOS ITENS ANTERIORES.</p>
  <p>5.7.2. RISCOS ASSOCIADOS À VIOLAÇÃO, OU POTENCIAL VIOLAÇÃO, PELO SEGURADO E/OU EVENTUAIS SÓCIOS OU ACIONISTAS, DIRETORES, EMPREGADOS, AGENTES PREPOSTOS, E OUTRAS PESSOAS QUE VENHAM A AGIR EM SEU NOME, DIRETA E INDIRETAMENTE, DOS DIREITOS HUMANOS, INCLUINDO, MAS NÃO SE LIMITANDO, A QUALQUER FORMA DE ABUSO HUMANO, SERVIDÃO, TRABALHO FORÇADO, TRABALHO COMPULSÓRIO, TRÁFICO HUMANO OU ESCRAVIDÃO EM SUAS ATIVIDADES COMERCIAIS.</p>
  <p> </p>
  <p>5.8. RISCOS RELACIONADOS À IRRIGAÇÃO</p>
  <p>5.8.1. PERDAS OCORRIDAS EM LAVOURAS COM IRRIGAÇÃO POR INUNDAÇÃO (“BANHO”), O QUAL DEFINE-SE PELA APLICAÇÃO DE ÁGUA AO SOLO, EM FORMA DE LÂMINA DE ÁGUA ESTAGNADA OU CONTÍNUA. ESTA CLÁUSULA NÃO SE APLICA À CULTURA DE ARROZ;</p>
  <p>5.8.2. SECA, DEVIDO À FALHA OU INTERRUPÇÃO DO EQUIPAMENTO DE IRRIGAÇÃO POR QUALQUER MOTIVO OU DANO ELÉTRICO OU MECÂNICO;</p>
  <p>5.8.3. SECA, DEVIDO À FALTA DE ÁGUA DETERMINADA POR FONTES INSUFICIENTES DE CAPTAÇÃO DE CULTIVOS IRRIGADOS;</p>
  <p>5.8.4. PERDAS DEVIDAS À FITOTOXICIDADE DE PESTICIDAS AGRÍCOLAS AO APLICAR PRODUTOS POR MEIO DE EQUIPAMENTOS DE IRRIGAÇÃO;</p>
  <p>5.8.5. NÃO ADOÇÃO DE SERVIÇOS ADEQUADOS DE IRRIGAÇÃO E DRENAGEM, QUANDO AS CONDIÇÕES DO SOLO, CLIMA E TIPO DE CULTIVO REQUEREREM ESTA TECNOLOGIA;</p>
  <p>5.8.6. PERDAS CAUSADAS PELO USO DE ÁGUA DE IRRIGAÇÃO DE MÁ QUALIDADE; E</p>
  <p>5.8.7. CONTAMINAÇÃO E/OU SALINIZAÇÃO DO SOLO COMO CONSEQUÊNCIA DO USO INADEQUADO DO SISTEMA DE IRRIGAÇÃO.</p>
  <p> </p>
  <p>5.9. EM CASO DE CONFLITO ENTRE AS EXCLUSÕES GERAIS PREVISTAS NESTA CLÁUSULA E</p>
</div>
""",


        """
<div class=\"text-block text-block-signature-page\" style=\"font-weight: 700;\">
  <p>AS EXCLUSÕES OU COBERTURAS PREVISTAS NAS CONDIÇÕES ESPECIAIS OU ADICIONAIS DESTE CONTRATO, PREVALECERÁ SEMPRE O DISPOSTO NAS CONDIÇÕES ESPECIAIS OU ADICIONAIS PARA A RESPECTIVA COBERTURA.</p>
  <p> </p>
  <p>5.10. AS CLÁUSULAS REFERENTES A EXCLUSÃO DE RISCOS E PREJUÍZOS OU QUE IMPLIQUEM LIMITAÇÃO OU PERDA DE DIREITOS E GARANTIAS SÃO DE INTERPRETAÇÃO RESTRITIVA QUANTO À SUA INCIDÊNCIA E ABRANGÊNCIA.</p>
</div>

<div class=\"signature signature-near-footer\">
  {signature_markup}
  <div class=\"line\" style=\"width: 60%; margin: 4px auto;\"></div>
  <div class=\"signature-role\">Diretora - Presidente</div>
  <div class=\"signature-place\">
    <span>Local: Rio de Janeiro</span>
    <span>{issue_date}</span>
  </div>
</div>
""".format(issue_date=escape(signature_issue_date), signature_markup=signature_markup),
    ]


def _build_header(
    data: PolicyDocumentData,
    logo_uri: str,
    header_uri: str,
    page_number: int,
    total_pages: int,
) -> str:
    if header_uri:
        return f"""
<div class=\"title-row title-row-banner\">
  <img class="header-banner" src="{escape(header_uri)}" alt="Header ESSOR" />
  <div class="header-center-title">SEGURO AGRÍCOLA</div>
  <div class="header-policy-title">APÓLICE</div>
  <div class="page-indicator page-indicator-banner">Página {page_number} de {total_pages}</div>
</div>

<div class=\"insurer-line\">ESSOR SEGUROS S.A. Cód. Seguradora (SUSEP): 1490 Cód. Seguradora (MAPA): 12<br/>CNPJ: 14.525.684/0001-50 &nbsp;&nbsp; RAMO: 1111 - SEGURO AGRÍCOLA</div>
<div class=\"line\"></div>
<table class=\"meta-grid\">
  <tr>
    <td><span class=\"label\">Nº Proposta:</span> {escape(data.proposal_number)}</td>
    <td class="meta-line-compact"><span class="label">Nº Apólice:</span> {escape(data.policy_number)} &nbsp;&nbsp; <span class="label">Endosso:</span> {escape(data.endorsement_number)}</td>
  </tr>
  <tr>
    <td><span class=\"label\">Data da Emissão:</span> {escape(data.issue_date)}</td>
    <td><span class="label">Sucursal:</span> {escape(data.branch)}</td>
  </tr>
  <tr>
    <td><span class="label">Safra:</span> {escape(data.harvest)}</td>
    <td><span class="label">Processo SUSEP nº:</span> {escape(data.susep_process)}</td>
  </tr>
  <tr>
    <td><span class="label">Produto:</span> {escape(data.product)}</td>
    <td><span class="label">Cobertura Principal:</span> {escape(data.main_coverage)}</td>
  </tr>
</table>
<div class=\"line\"></div>
"""

    return f"""
<div class=\"title-row\">
  <img class=\"logo\" src=\"{escape(logo_uri)}\" alt=\"Logo ESSOR\" />
  <div class=\"doc-title\">SEGURO AGRÍCOLA APÓLICE</div>
  <div class=\"page-indicator\">Página {page_number} de {total_pages}</div>
</div>

<div class=\"insurer-line\">ESSOR SEGUROS S.A. Cód. Seguradora (SUSEP): 1490 Cód. Seguradora (MAPA): 12<br/>CNPJ: 14.525.684/0001-50 &nbsp;&nbsp; RAMO: 1111 - SEGURO AGRÍCOLA</div>
<div class=\"line\"></div>
<table class=\"meta-grid\">
  <tr>
    <td><span class=\"label\">Nº Proposta:</span> {escape(data.proposal_number)}</td>
    <td class="meta-line-compact"><span class="label">Nº Apólice:</span> {escape(data.policy_number)} &nbsp;&nbsp; <span class="label">Endosso:</span> {escape(data.endorsement_number)}</td>
  </tr>
  <tr>
    <td><span class=\"label\">Data da Emissão:</span> {escape(data.issue_date)}</td>
    <td><span class="label">Sucursal:</span> {escape(data.branch)}</td>
  </tr>
  <tr>
    <td><span class="label">Safra:</span> {escape(data.harvest)}</td>
    <td><span class="label">Processo SUSEP nº:</span> {escape(data.susep_process)}</td>
  </tr>
  <tr>
    <td><span class="label">Produto:</span> {escape(data.product)}</td>
    <td><span class="label">Cobertura Principal:</span> {escape(data.main_coverage)}</td>
  </tr>
</table>
<div class=\"line\"></div>
"""


def _build_footer(footer_uri: str) -> str:
    if footer_uri:
        return f"""
<img class=\"footer-banner\" src=\"{escape(footer_uri)}\" alt=\"Rodapé ESSOR\" />
"""

    return " "


def _chunk(values: list[list[str]], size: int) -> list[list[list[str]]]:
    if size <= 0:
        return [values]
    return [values[index : index + size] for index in range(0, len(values), size)]


def _row_cell(row: list[str], index: int, default: str = "-") -> str:
  if 0 <= index < len(row):
    value = str(row[index]).strip()
    return value or default
  return default


def _beneficiary_document(beneficiary: object) -> str:
  cpf_or_cnpj = str(getattr(beneficiary, "cpf", "")).strip()
  if cpf_or_cnpj:
    return cpf_or_cnpj
  legacy_value = str(getattr(beneficiary, "document", "")).strip()
  return legacy_value or "Não informado"


def _beneficiary_share(beneficiary: object) -> str:
  share = str(getattr(beneficiary, "percentage", "")).strip()
  if not share:
    share = str(getattr(beneficiary, "share", "")).strip()
  if share.endswith("%"):
    share = share[:-1].strip()
  return share or "0"


def _format_date_with_full_month_name(date_text: str) -> str:
    match = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", (date_text or "").strip())
    if not match:
        return date_text

    day, month, year = match.groups()
    month_index = int(month)
    if month_index < 1 or month_index > 12:
        return date_text

    return f"{day} de {_PT_BR_MONTH_NAMES[month_index - 1]} de {year}"


def _social_name_or_dash(value: str | None) -> str:
    normalized = str(value or "").strip()
    if not normalized:
        return "-"

    normalized_compact = " ".join(normalized.casefold().split())
    normalized_compact = normalized_compact.rstrip(" .;:,-_")
    if normalized_compact in {"não informado", "nao informado"}:
        return "-"

    return normalized


def _normalize_brazilian_state_code(raw_state: str) -> str:
    normalized = (raw_state or "").strip()
    if not normalized:
        return ""

    if normalized.isdigit():
        return _BRAZILIAN_STATE_CODES_BY_ID.get(int(normalized), normalized)

    normalized_upper = normalized.upper()
    if normalized_upper in _BRAZILIAN_STATE_CODES:
        return normalized_upper

    return normalized


def _format_city_state(city_state: str | None) -> str:
    raw = (city_state or "").strip()
    if not raw:
        return "Não informado"

    if "/" in raw:
        city, state = raw.rsplit("/", maxsplit=1)
        city_name = city.strip()
        normalized_state = _normalize_brazilian_state_code(state)
        if not city_name:
            return normalized_state or "Não informado"
        return f"{city_name}/{normalized_state}" if normalized_state else city_name

    if " - " in raw:
        city, state = raw.rsplit(" - ", maxsplit=1)
        city_name = city.strip()
        normalized_state = _normalize_brazilian_state_code(state)
        if not city_name:
            return normalized_state or "Não informado"
        return f"{city_name}/{normalized_state}" if normalized_state else city_name

    normalized = _normalize_brazilian_state_code(raw)
    return normalized or "Não informado"


def _asset_uri(path: str | None) -> str:
    if not path:
        return ""

    candidate = Path(path)
    if not candidate.exists():
        return ""

    return candidate.resolve().as_uri()


def _first_existing_path(*paths: str | None) -> str | None:
    for path in paths:
        if path and Path(path).exists():
            return path
    return None
