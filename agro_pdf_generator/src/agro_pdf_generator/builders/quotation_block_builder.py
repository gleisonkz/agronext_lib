import agronext_procurement as procurement

from ..blocks import BlockConfig, BlockType, DataTableVariant
from ..config import Spacing
from ..schemas import PDFData


class QuotationBlockBuilder:
    def __init__(self, data: PDFData):
        self._data = data

    def build_all(self) -> list[BlockConfig]:
        blocks = [
            self._build_logo_block(),
            self._build_header_block(),
            self._build_applicant_block(),
            # Na cotação, não incluímos endereço de residência e exposição política
            self._build_coverage_block(),
            self._build_payment_block(),
            self._build_installments_block(),
            self._build_broker_block(),
            self._build_property_block(),
            self._build_risk_block(),
            self._build_coordinates_block(),
        ]

        croqui = self._build_croqui_block()
        if croqui:
            blocks.append(croqui)

        blocks.append(self._build_risk_questionnaire_block())
        blocks.append(self._build_propopent_notifications())
        blocks.append(self._build_declarations_and_commitments())

        return blocks

    def _build_logo_block(self) -> BlockConfig:
        return BlockConfig(
            type=BlockType.LOGO,
            estimated_height=70,
            repeat_on_pages=True,  # Controlado por stops_header_repeat no proponent_declaration
            keep_space_when_hidden=True,  # Mantém espaço mesmo quando header para
            logo_path=self._data.header.logo_path,
        )

    def _build_header_block(self) -> BlockConfig:
        h = self._data.header
        return BlockConfig(
            type=BlockType.INFO_TABLE,
            estimated_height=150,
            repeat_on_pages=True,
            no_margin=False,
            rows=[
                [
                    {
                        "label": "Cotação de Seguro Nº",
                        "value": self._format_proposal_number(h.proposal_number),
                        "width": "17%",
                    },
                    {
                        "label": "Data da Cotação",
                        "value": h.reception_date,
                        "width": "22%",
                    },
                    {
                        "label": "Versão",
                        "value": f"1.0.0 - Data: {h.reception_date}",
                        "width": "28%",
                    },
                    {
                        "label": "",
                        "value": "COTAÇÃO SEM COBERTURA",
                        "width": "23%",
                        "background_color": "#FEF2F2",
                        "text_color": "#B91C1C",
                    },
                    {"label": "Página", "value": "{{page}}", "width": "10%"},
                ],
                [
                    {
                        "label": "Cobertura Principal",
                        "value": h.main_coverage,
                        "width": "20%",
                    },
                    {"label": "Cultura", "value": h.crop, "width": "20%"},
                    {"label": "BACEN", "value": h.bacen_code, "width": "35%"},
                    {"label": "Safra", "value": h.harvest, "width": "25%"},
                ],
                [
                    {"label": "Seguradora", "value": h.insurer, "width": "25%"},
                    {
                        "label": "CNPJ",
                        "value": self._format_cpf_or_cnpj(h.insurer_cnpj),
                        "width": "25%",
                    },
                    {"label": "SUSEP", "value": h.susep, "width": "25%"},
                    {"label": "Código MAPA", "value": h.mapa_code, "width": "25%"},
                ],
            ],
        )

    def _build_applicant_block(self) -> BlockConfig:
        p = self._data.applicant
        document = "".join(char for char in (p.cpf or "").upper() if char.isalnum())
        is_cnpj = len(document) == 14

        rows = [
                [
                    {"label": "Nome/ Razão social", "value": p.name, "width": "25%"},
                    {
                        "label": "CPF/CNPJ",
                        "value": self._format_cpf_or_cnpj(p.cpf),
                        "width": "25%",
                    },
                    {
                        "label": "Data de nascimento",
                        "value": p.birth_date,
                        "width": "25%",
                    },
                    {"label": "Nome social", "value": p.social_name, "width": "25%"},
                ],
        ]

        if not is_cnpj:
            rows.append([
                {
                    "label": "Documento",
                    "value": "RG",
                    "width": "25%",
                },
                {
                    "label": "RG",
                    "value": p.document_number,
                    "width": "25%",
                },
                {
                    "label": "Órgão expedidor",
                    "value": p.issuing_authority,
                    "width": "25%",
                },
                {
                    "label": "Data de expedição",
                    "value": p.issue_date,
                    "width": "25%",
                },
            ])
        
        rows.append([
            {"label": "E-mail", "value": p.main_email, "width": "25%"},
            {
                "label": "Telefone",
                "value": self._format_phone(p.phone_number),
                "width": "25%",
            },
            {
                "label": "Tipo",
                "value": p.phone_type,
                "width": "25%",
            },
            {"label": "WhatsApp", "value": p.is_whatsapp, "width": "25%"},
        ])

        if is_cnpj:
            rows.append([
                {
                    "label": "Atividade economica",
                    "value": p.business_activity,
                    "width": "33.33%",
                },
                {
                    "label": "Receita operacional brutal anual",
                    "value": p.annual_gross_revenue,
                    "width": "33.33%",
                },
                {
                    "label": "Patrimonio liquido",
                    "value": p.net_worth,
                    "width": "33.34%",
                },
            ])
        else:
            rows.append([
                {
                    "label": "Profissão",
                    "value": p.professional_category,
                    "width": "50%",
                },
                {"label": "Renda mensal", "value": p.income, "width": "50%"},
            ])

        return BlockConfig(
            type=BlockType.INFO_TABLE,
            section_header="Dados Iniciais",
            estimated_height=140,
            rows=rows,
        )

    def _build_address_block(self) -> BlockConfig:
        e = self._data.residential_address
        return BlockConfig(
            type=BlockType.INFO_TABLE,
            section_header="Endereço de Residência",
            estimated_height=120,
            rows=[
                [
                    {
                        "label": "Cep",
                        "value": self._format_zip_code(e.zip_code),
                        "width": "20%",
                    },
                    {
                        "label": "País",
                        "value": self._format_country(e.country),
                        "width": "20%",
                    },
                    {
                        "label": "Estado",
                        "value": self._format_state(e.state),
                        "width": "20%",
                    },
                    {"label": "Município", "value": e.city, "width": "20%"},
                    {"label": "Bairro", "value": e.neighborhood, "width": "20%"},
                ],
                [
                    {"label": "Logradouro", "value": e.street, "width": "33.33%"},
                    {"label": "Número", "value": e.number, "width": "33.33%"},
                    {"label": "Complemento", "value": e.complement, "width": "33.34%"},
                ],
            ],
        )

    def _build_coverage_block(self) -> BlockConfig:
        c = self._data.coverage
        return BlockConfig(
            type=BlockType.INFO_TABLE,
            section_header="Cobertura Principal",
            estimated_height=140,
            row_gap_after=[0],
            rows=[
                [
                    {"label": "Cobertura", "value": c.name, "width": "13%"},
                    {
                        "label": "LMGA (R$)",
                        "value": c.policy_limit_brl,
                        "width": "11%",
                    },
                    {
                        "label": "Franquia (%)",
                        "value": c.deductible_pct,
                        "width": "11%",
                    },
                    {"label": "Taxa (%)", "value": c.coverage_rate_pct, "width": "8%"},
                    {
                        "label": "Prêmio tarifário (R$)",
                        "value": c.tariff_premium,
                        "width": "17%",
                    },
                    {
                        "label": "Área segurada (ha)",
                        "value": self._format_decimal_separator(c.insured_area_ha),
                        "width": "16%",
                    },
                    {
                        "label": "Quadra/Talhão segurados (qtd)",
                        "value": c.plot_count.rjust(2, "0"),
                        "width": "24%",
                    },
                ],
                [
                    {
                        "label": "Prêmio líquido aproximado (R$)",
                        "value": c.net_premium,
                        "width": "25%",
                    },
                    {
                        "label": "Subvenção federal (R$)",
                        "value": c.federal_subsidy_brl,
                        "width": "23%",
                    },
                    {
                        "label": "Subvenção estadual (R$)",
                        "value": c.state_subsidy_brl,
                        "width": "25%",
                    },
                    {
                        "label": "Valor proponente aproximado (R$)",
                        "value": c.applicant_value,
                        "width": "27%",
                    },
                ],
            ],
        )

    def _build_payment_block(self) -> BlockConfig:
        pg = self._data.payment
        return BlockConfig(
            type=BlockType.INFO_TABLE,
            section_header="Formas de Pagamento",
            estimated_height=80,
            rows=[
                [
                    {
                        "label": "Forma de pagamento",
                        "value": pg.payment_method,
                        "width": "16.66%",
                    },
                    {
                        "label": "Número de parcelas",
                        "value": pg.number_of_installments,
                        "width": "16.66%",
                    },
                    {
                        "label": "Prêmio Líquido (R$)",
                        "value": pg.net_premium,
                        "width": "16.66%",
                    },
                    {
                        "label": "Custo de Apólice (R$)",
                        "value": pg.policy_cost,
                        "width": "16.66%",
                    },
                    {"label": "IOF", "value": pg.iof, "width": "16.66%"},
                    {
                        "label": "Prêmio a Pagar (R$)",
                        "value": pg.total_premium,
                        "width": "16.70%",
                    },
                ]
            ],
        )

    def _build_installments_block(self) -> BlockConfig:
        return BlockConfig(
            type=BlockType.DATA_TABLE,
            section_header="Parcelamento",
            estimated_height=50 + len(self._data.payment.installments) * 30,
            headers=[
                "Número da parcela",
                "Prêmio proponente (R$)",
                "Data do vencimento",
            ],
            data_rows=self._data.payment.installments,
            widths=["33.33%", "33.33%", "33.34%"],
            variant=DataTableVariant.CENTERED_NORMAL,
        )

    def _build_broker_block(self) -> BlockConfig:
        b = self._data.broker
        emails = self._format_list_items(b.emails)
        phones = self._format_list_items(b.phones)

        return BlockConfig(
            type=BlockType.INFO_TABLE,
            section_header="Corretora",
            estimated_height=100,
            row_gap_after=[0],
            rows=[
                [
                    {"label": "Nome", "value": b.name, "width": "25%"},
                    {"label": "Número SUSEP", "value": b.susep, "width": "25%"},
                    {
                        "label": "Participação",
                        "value": b.social_name,
                        "width": "25%",
                    },
                    {
                        "label": "Telefone",
                        "value": b.phone,
                        "width": "25%",
                    },
                ],
                [
                    {"label": "E-mail", "value": emails, "width": "50%"},
                    {"label": "Telefone", "value": phones, "width": "50%"},
                ],
            ],
        )

    def _build_property_block(self) -> BlockConfig:
        prop = self._data.property
        return BlockConfig(
            type=BlockType.INFO_TABLE,
            section_header="Dados da Propriedade",
            estimated_height=180,
            force_page_break=True,  # Forçar início na página 2
            rows=[
                [
                    {
                        "label": "Nome da propriedade",
                        "value": prop.name,
                        "width": "50%",
                    },
                    {
                        "label": "Tipo de proponente",
                        "value": prop.ownership_type,
                        "width": "25%",
                    },
                    {"label": "Coordenadas", "value": prop.coordinates, "width": "25%"},
                ],
                [
                    {
                        "label": "Cep",
                        "value": self._format_zip_code(prop.zip_code),
                        "width": "20%",
                    },
                    {
                        "label": "País",
                        "value": self._format_country(prop.country),
                        "width": "20%",
                    },
                    {
                        "label": "Estado",
                        "value": self._format_state(prop.state),
                        "width": "20%",
                    },
                    {"label": "Município", "value": prop.city, "width": "20%"},
                    {
                        "label": "BACEN do município",
                        "value": prop.bacen_code,
                        "width": "20%",
                    },
                ],
                [
                    {"label": "Bairro", "value": prop.neighborhood, "width": "33.33%"},
                    {"label": "Logradouro", "value": prop.street, "width": "33.33%"},
                    {"label": "Número", "value": prop.number, "width": "33.34%"},
                ],
            ],
        )

    def _build_risk_block(self) -> BlockConfig:
        return BlockConfig(
            type=BlockType.DATA_TABLE,
            section_header="Descrição do Risco",
            estimated_height=50 + len(self._data.risk_data) * 35,
            headers=[
                "Quadra/ Talhão",
                "ID Quadra/ Talhão",
                "Número do Item",
                "Variedade",
                "Área (ha)",
                "Produtividade (ton/ha)",
                "Valor por Tonelada (R$)",
                "LMGA Parcial (R$)",
                "Franquia Parcial (R$)",
                "Prêmio Parcial (R$)",
            ],
            data_rows=self._data.risk_data,
            widths=[
                "10%",
                "10%",
                "10%",
                "10%",
                "8%",
                "12%",
                "10%",
                "10%",
                "10%",
                "10%",
            ],
            variant=DataTableVariant.SMALL_CENTERED_UPPERCASE,
        )

    def _build_coordinates_block(self) -> BlockConfig:
        return BlockConfig(
            type=BlockType.DATA_TABLE,
            estimated_height=50 + len(self._data.plot_coordinates) * 30,
            headers=["Quadra/ Talhão", "Ponto central do polígono"],
            data_rows=self._data.plot_coordinates,
            widths=["50%", "50%"],
            variant=DataTableVariant.CENTERED_NORMAL,
        )

    def _build_croqui_block(self) -> BlockConfig | None:
        # croqui_bytes is now raw image bytes.  refuse to build if empty.
        croqui = getattr(self._data, "croqui_bytes", None)
        if not croqui:
            return None
        # provide bytes to the block; renderer will do the base64 conversion.
        return BlockConfig(
            type=BlockType.IMAGE,
            section_header="Croqui",
            estimated_height=400,
            image_bytes=croqui,
        )

    def _build_declarations_and_commitments(self) -> BlockConfig:
        html_content = self._data.declarations_and_commitments_html_block
        estimated_lines = len(html_content) / 120
        estimated_height = int(estimated_lines * 20 + html_content.count("</p>") * 8)
        # Minimum height of 50px, no maximum cap to allow proper page breaks
        estimated_height = max(50, estimated_height)

        block = BlockConfig(
            type=BlockType.HTML_BLOCK,
            section_header="DECLARAÇÕES E COMPROMISSOS DO PROPONENTE RELACIONADAS À EXECUÇÃO E CONFORMIDADE CONTRATUAL",
            estimated_height=estimated_height,
            content=html_content,
        )

        return block

    def _build_propopent_notifications(self) -> BlockConfig:

        html_content = self._data.propopent_notifications_html_block
        estimated_lines = len(html_content) / 120
        estimated_height = int(estimated_lines * 20 + html_content.count("</p>") * 8)
        # Minimum height of 50px, no maximum cap to allow proper page breaks
        estimated_height = max(50, estimated_height)

        block = BlockConfig(
            type=BlockType.HTML_BLOCK,
            section_header="Avisos Importantes para o Proponente",
            estimated_height=estimated_height,
            content=html_content,
        )

        return block

    def _build_risk_questionnaire_block(self) -> BlockConfig:
        rq = self._data.risk_questionnaire
        section_second_header = None
        if rq.attention_title or rq.attention_text:
            section_second_header = (
                f'<div style="font-weight: 600;">{rq.attention_title}</div>'
                f"<div>{rq.attention_text}</div>"
            )

        # Build rows for INFO_TABLE - each question is one row with full width
        rows = []
        for i, q in enumerate(rq.questions, 1):
            # Build the value with question, answer, and extra fields
            value_parts = [f'<div style="font-weight: 600;">{i} - {q.question}</div>']
            value_parts.append(f"<div>Resposta: {q.answer}</div>")

            for label, value in q.extra_fields:
                value_parts.append(f"<div>{label}: {value}</div>")

            rows.append([{"label": "", "value": "".join(value_parts), "width": "100%"}])

        return BlockConfig(
            type=BlockType.INFO_TABLE,
            section_header="Questionário de Risco",
            section_second_header=section_second_header,
            estimated_height=(150 if section_second_header else 50) + len(rq.questions) * 60,
            rows=rows,
            force_page_break=True,
        )

    def _format_list_items(self, items: list[str]) -> str:
        return "".join(
            f'<div style="margin-bottom: {Spacing.MD};">{item}</div>'
            if i < len(items) - 1
            else f"<div>{item}</div>"
            for i, item in enumerate(items)
        )

    def _format_zip_code(self, zip_code: str | None) -> str:
        if not zip_code:
            return ""

        digits = "".join(char for char in zip_code if char.isdigit())
        if len(digits) != 8:
            return zip_code

        return f"{digits[:5]}-{digits[5:]}"

    def _format_country(self, country: str | None) -> str:
        if not country:
            return ""

        country_code = country.strip().upper()
        if country_code in procurement.CountryDisplayNames.__members__:
            return procurement.CountryDisplayNames[country_code].value

        return country

    def _format_state(self, state: str | None) -> str:
        if not state:
            return ""

        state_code = state.strip().upper()
        if state_code in procurement.BrazilianStateDisplayNames.__members__:
            return procurement.BrazilianStateDisplayNames[state_code].value

        return state

    def _format_decimal_separator(self, value: str | None) -> str:
        if not value:
            return ""

        trimmed = value.strip()
        if "," in trimmed:
            return value

        if trimmed.count(".") == 1:
            integer_part, decimal_part = trimmed.split(".", 1)
            if integer_part.isdigit() and decimal_part.isdigit():
                return f"{integer_part},{decimal_part}"

        return value

    def _format_proposal_number(self, proposal_number: str | None) -> str:
        if not proposal_number:
            return "Não informado"

        digits = "".join(char for char in proposal_number if char.isdigit())
        if len(digits) != 15:
            return proposal_number

        return f"{digits[0]}.{digits[1:4]}.{digits[4:8]}.{digits[8:14]}-{digits[14]}"

    def _format_cpf_or_cnpj(self, document: str | None) -> str:
        if not document:
            return "Não informado"

        sanitized = "".join(char for char in document.upper() if char.isalnum())

        if len(sanitized) == 11 and sanitized.isdigit():
            return (
                f"{sanitized[:3]}.{sanitized[3:6]}.{sanitized[6:9]}-"
                f"{sanitized[9:]}"
            )

        # CNPJ now supports alphanumeric content, so we validate by length only.
        if len(sanitized) == 14:
            return (
                f"{sanitized[:2]}.{sanitized[2:5]}.{sanitized[5:8]}/"
                f"{sanitized[8:12]}-{sanitized[12:]}"
            )

        return document

    def _format_phone(self, phone: str | None) -> str:
        if not phone:
            return ""

        digits = "".join(char for char in phone if char.isdigit())

        if digits.startswith("55") and len(digits) in {12, 13}:
            digits = digits[2:]

        if len(digits) == 11:
            return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"

        if len(digits) == 10:
            return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"

        return phone

