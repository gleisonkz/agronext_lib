import agronext_procurement as procurement
from datetime import date
from decimal import Decimal, InvalidOperation
from html import escape
import re

from ..blocks import BlockConfig, BlockType, DataTableVariant
from ..config import Spacing
from ..schemas import PDFData
from ..utils import format_monetary_value


class ProposalBlockBuilder:
    def __init__(self, data: PDFData):
        self._data = data

    def build_all(self) -> list[BlockConfig]:
        blocks = [
            self._build_logo_block(),
            self._build_header_block(),
            self._build_applicant_block(),
            self._build_address_block(),
            self._build_political_exposure_block(),
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

        blocks.extend(
            [
                self._build_risk_questionnaire_block(),
                self._build_subsidy_block(),
                self._build_beneficiaries_block(),
                self._build_authorized_persons_block(),
            ]
        )

        observations = self._build_observations_block()
        if observations:
            blocks.append(observations)

        # Add proponent notifications block (replaces information section)
        proponent_notifications = self._build_proponent_notifications_block()
        if proponent_notifications:
            blocks.extend(proponent_notifications)

        # Add grace period block
        grace_period = self._build_grace_period_block()
        if grace_period:
            blocks.append(grace_period)

        # Replace coverage restrictions with excluded risks section
        excluded_risks = self._build_excluded_risks_block()
        if excluded_risks:
            blocks.append(excluded_risks)

        # Replace available documents with broker declarations section
        broker_declarations = self._build_proponent_declaration_block()
        if broker_declarations:
            blocks.extend(broker_declarations)

        # Replace excluded risks page with proponent declarations and commitments
        declarations_and_commitments = self._build_declarations_and_commitments_block()
        if declarations_and_commitments:
            blocks.extend(declarations_and_commitments)

        # Add authorization term block
        authorization_term = self._build_authorization_term_block()
        if authorization_term:
            blocks.extend(authorization_term)

        # Add authorization beneficiary block
        authorization_beneficiary = self._build_authorization_beneficiary_block()
        if authorization_beneficiary:
            blocks.extend(authorization_beneficiary)

        # Add state subsidy term block
        state_subsidy_term = self._build_state_subsidy_term_block()
        if state_subsidy_term:
            blocks.extend(state_subsidy_term)

        # Add state authorization term block
        state_authorization_term = self._build_state_authorization_term_block()
        if state_authorization_term:
            blocks.extend(state_authorization_term)

        # Add federal subsidy term block
        federal_subsidy_term = self._build_federal_subsidy_term_block()
        if federal_subsidy_term:
            blocks.extend(federal_subsidy_term)

        return blocks

    def _build_logo_block(self) -> BlockConfig:
        return BlockConfig(
            type=BlockType.LOGO,
            estimated_height=70,
            repeat_on_pages=True,  # Controlado por stops_header_repeat no proponent_declaration
            keep_space_when_hidden=True,
            logo_path=self._data.header.logo_path,
        )

    def _build_header_block(self) -> BlockConfig:
        h = self._data.header
        return BlockConfig(
            type=BlockType.INFO_TABLE,
            estimated_height=150,
            repeat_on_pages=True,  # Controlado por stops_header_repeat no proponent_declaration
            no_margin=False,
            rows=[
                [
                    {
                        "label": "Proposta de seguro Nº",
                        "value": self._format_proposal_number(h.proposal_number),
                        "width": "18%",
                    },
                    {
                        "label": "Data da recepção da proposta",
                        "value": h.reception_date,
                        "width": "23%",
                    },
                    {
                        "label": "Vigência do contrato de seguro",
                        "value": h.validity_period,
                        "width": "49%",
                    },
                    {"label": "Página", "value": "{{page}}", "width": "10%"},
                ],
                [
                    {
                        "label": "Cobertura principal",
                        "value": h.main_coverage,
                        "width": "20%",
                    },
                    {"label": "Cultura", "value": h.crop, "width": "27%"},
                    {"label": "BACEN", "value": h.bacen_code, "width": "26%"},
                    {"label": "Safra", "value": h.harvest, "width": "27%"},
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
                        "label": "CEP",
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

    def _build_political_exposure_block(self) -> BlockConfig:
        exp = self._data.political_exposure
        pep_text = (
            "Circular SUSEP Nº 612/2020: pessoas politicamente expostas (PPE) são aquelas que ocupam ou "
            "ocuparam, nos últimos cinco anos, cargos, empregos ou funções públicas relevantes. "
            "Isso inclui também funções em organizações internacionais."
        )
        return BlockConfig(
            type=BlockType.INFO_TABLE,
            section_header="Exposição Política",
            estimated_height=100,
            rows=[
                [
                    {
                        "label": "O proponente é pessoa politicamente exposta?",
                        "value": exp.is_pep,
                        "width": "100%",
                    }
                ],
                [
                    {
                        "label": "Pessoa física - Politicamente exposta",
                        "value": pep_text,
                        "width": "100%",
                    }
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
            force_page_break=True,
            estimated_height=180,
            rows=[
                [
                    {
                        "label": "Nome da propriedade",
                        "value": prop.name,
                        "width": "50%",
                    },
                    {
                        "label": "Tipo de Proponente",
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
        formatted_coordinates = [
            [row[0].rjust(2, "0"), *row[1:]] if row else row
            for row in self._data.plot_coordinates
        ]

        return BlockConfig(
            type=BlockType.DATA_TABLE,
            estimated_height=50 + len(self._data.plot_coordinates) * 30,
            headers=["Quadra/ Talhão", "Ponto central do polígono"],
            data_rows=formatted_coordinates,
            widths=["50%", "50%"],
            variant=DataTableVariant.CENTERED_NORMAL,
        )

    def _build_croqui_block(self) -> BlockConfig | None:
        croqui = getattr(self._data, "croqui_bytes", None)
        if not croqui:
            return None
        return BlockConfig(
            type=BlockType.IMAGE,
            section_header="Croqui",
            estimated_height=400,
            image_bytes=croqui,
        )

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

    def _build_subsidy_block(self) -> BlockConfig:
        s = self._data.subsidy

        # Build rows for INFO_TABLE - each question is one row with full width
        rows = []
        for q in s.questions:
            # Build the value with question, answer, and extra fields
            value_parts = [f'<div style="font-weight: 600;">{q.question}</div>']
            value_parts.append(f"<div>Resposta: {q.answer}</div>")

            for label, value in q.extra_fields:
                value_parts.append(f"<div>{label}: {value}</div>")

            rows.append([{"label": "", "value": "".join(value_parts), "width": "100%"}])

        return BlockConfig(
            type=BlockType.INFO_TABLE,
            section_header="Subvenção",
            estimated_height=50 + len(s.questions) * 60,
            rows=rows,
        )

    def _build_beneficiaries_block(self) -> BlockConfig:
        if not self._data.beneficiaries:
            return BlockConfig(
                type=BlockType.INFO_TABLE,
                section_header="Beneficiário(s)",
                estimated_height=50,
                rows=[],
            )

        # Build rows for INFO_TABLE - each beneficiary has 2 rows
        rows = []
        row_gap_after = []
        premium_amount = self._get_beneficiary_premium_base()

        for i, b in enumerate(self._data.beneficiaries):
            percentage_value = self._parse_percentage(b.percentage)
            formatted_percentage = self._format_percentage(b.percentage)
            calculated_value = self._calculate_beneficiary_value(
                premium_amount,
                percentage_value,
            )

            # Row 1: Beneficiário N + Name | CPF | Data de nascimento | Nome social
            rows.append(
                [
                    {
                        "label": f"Beneficiário {i + 1:02d}",
                        "value": b.name,
                        "width": "25%",
                    },
                    {
                        "label": "CPF/CNPJ",
                        "value": self._format_cpf_or_cnpj(b.cpf),
                        "width": "25%",
                    },
                    {
                        "label": "Data de nascimento",
                        "value": b.birth_date,
                        "width": "25%",
                    },
                    {"label": "Nome social", "value": b.social_name, "width": "25%"},
                ]
            )

            # Row 2: E-mail | Telefone | Porcentagem (%) | Valor (R$) | Relação
            rows.append(
                [
                    {"label": "E-mail", "value": b.email, "width": "20%"},
                    {
                        "label": "Telefone",
                        "value": self._format_phone(b.phone),
                        "width": "20%",
                    },
                    {
                        "label": "Porcentagem (%)",
                        "value": formatted_percentage,
                        "width": "20%",
                    },
                    {
                        "label": "Valor (R$)",
                        "value": calculated_value,
                        "width": "20%",
                    },
                    {"label": "Relação", "value": b.relationship, "width": "20%"},
                ]
            )

            # Add gap after each beneficiary's second row (except the last one)
            if i < len(self._data.beneficiaries) - 1:
                row_gap_after.append(len(rows) - 1)

        return BlockConfig(
            type=BlockType.INFO_TABLE,
            section_header="Beneficiário(s)",
            estimated_height=50 + len(self._data.beneficiaries) * 80,
            rows=rows,
            row_gap_after=row_gap_after,
        )

    def _build_authorized_persons_block(self) -> BlockConfig:
        # Build rows for INFO_TABLE
        rows = []

        # First row: question about authorized persons (separate block)
        question = "Há representante(s) do proponente a acompanhar a(s) vistoria(s)?"
        value_parts = [f'<div style="font-weight: 600;">{question}</div>']
        value_parts.append(f"<div>Resposta: {self._data.has_authorized_persons}</div>")
        rows.append([{"label": "", "value": "".join(value_parts), "width": "100%"}])

        # Add each authorized person - one row per person (all in same block)
        for p in self._data.authorized_persons:
            rows.append(
                [
                    {"label": "Nome", "value": p.name, "width": "33.33%"},
                    {"label": "Relação", "value": p.relationship, "width": "33.33%"},
                    {
                        "label": "Telefone",
                        "value": self._format_phone(p.phone),
                        "width": "33.34%",
                    },
                ]
            )

        # Gap after first row (question) to separate from persons list
        row_gap_after = [0] if self._data.authorized_persons else []

        return BlockConfig(
            type=BlockType.INFO_TABLE,
            section_header="Pessoa(s) Autorizada(s) para Vistoria",
            estimated_height=80 + len(self._data.authorized_persons) * 40,
            rows=rows,
            row_gap_after=row_gap_after,
        )

    def _build_observations_block(self) -> BlockConfig:
        if not self._data.observations:
            return

        observations = self._data.observations
        lines = observations.splitlines() or [observations]
        estimated_lines = sum(max(1, len(line) / 120) for line in lines)
        estimated_height = max(120, int(60 + estimated_lines * 20))
        wrapped_value = (
            '<span style="display: block; white-space: pre-wrap; '
            'overflow-wrap: anywhere; word-break: break-word;">'
            f"{escape(observations)}"
            "</span>"
        )

        # INFO_TABLE with one row, one column: label "Observações" (bold) and value with text
        # Section header is "Dados Complementares"
        return BlockConfig(
            type=BlockType.INFO_TABLE,
            section_header="Dados Complementares",
            estimated_height=estimated_height,
            rows=[
                [
                    {
                        "label": "Observações",
                        "value": wrapped_value,
                        "width": "100%",
                    }
                ]
            ],
        )

    def _build_grace_period_block(self) -> BlockConfig | None:
        if not self._data.grace_period_html:
            return None

        content = self._data.grace_period_html
        # Estimate height based on content length
        # ~120 chars per line at 14px on 1144px width
        estimated_lines = len(content) / 120
        estimated_height = int(estimated_lines * 20)
        estimated_height = max(80, estimated_height)

        return BlockConfig(
            type=BlockType.TEXT_BLOCK,
            section_header="Carência",
            estimated_height=estimated_height,
            content=content,
            text_bordered=False,
            text_bold=True,
        )

    def _build_coverage_restrictions_block(self) -> BlockConfig | None:
        if not self._data.coverage_restrictions_html:
            return None

        content = self._data.coverage_restrictions_html
        # Estimate height based on content length
        # ~120 chars per line at 14px on 1144px width
        estimated_lines = len(content) / 120
        estimated_height = int(estimated_lines * 20)
        estimated_height = max(80, estimated_height)

        return BlockConfig(
            type=BlockType.TEXT_BLOCK,
            section_header="Restrições para Cobertura dos Riscos",
            estimated_height=estimated_height,
            content=content,
            text_bordered=False,
            text_bold=True,
        )

    def _build_information_blocks(self) -> list[BlockConfig]:
        if not self._data.information_html_blocks:
            return []

        blocks = []
        for html_content in self._data.information_html_blocks:
            # Estimate height based on content length
            # ~100 chars per line at 16px on 1144px width, ~24px per line
            # Plus 16px margin between paragraphs
            estimated_lines = len(html_content) / 100
            estimated_height = int(
                estimated_lines * 24 + html_content.count("</p>") * 16
            )
            # Minimum height of 150px
            estimated_height = max(150, estimated_height)

            # Each block gets its own section header "Informações"
            blocks.append(
                BlockConfig(
                    type=BlockType.HTML_BLOCK,
                    section_header="Informações",
                    estimated_height=estimated_height,
                    content=html_content,
                )
            )

        return blocks

    def _estimate_html_block_height(
        self,
        html_content: str,
        *,
        minimum: int = 50,
        extra_padding: int = 0,
    ) -> int:
        estimated_lines = len(html_content) / 120
        estimated_height = int(estimated_lines * 20 + html_content.count("</p>") * 8)
        return max(minimum, estimated_height + extra_padding)

    def _split_html_into_chunks(
        self,
        html_content: str,
        *,
        max_chunk_height: int,
    ) -> list[str]:
        segments = [
            segment.strip()
            for segment in re.split(r"\n\s*\n", html_content)
            if segment.strip()
        ]
        if not segments:
            return [html_content]

        chunks: list[str] = []
        current_segments: list[str] = []
        current_height = 0

        for segment in segments:
            segment_height = self._estimate_html_block_height(segment, minimum=36)
            if current_segments and current_height + segment_height > max_chunk_height:
                chunks.append("\n\n".join(current_segments))
                current_segments = [segment]
                current_height = segment_height
                continue

            current_segments.append(segment)
            current_height += segment_height

        if current_segments:
            chunks.append("\n\n".join(current_segments))

        return chunks

    def _build_proponent_notifications_block(self) -> list[BlockConfig]:
        html_content = self._data.propopent_notifications_html_block
        if not html_content:
            return []

        chunks = self._split_html_into_chunks(html_content, max_chunk_height=1100)
        blocks: list[BlockConfig] = []
        for index, chunk in enumerate(chunks):
            blocks.append(
                BlockConfig(
                    type=BlockType.HTML_BLOCK,
                    section_header="Avisos Importantes para o Proponente",
                    estimated_height=self._estimate_html_block_height(chunk),
                    content=chunk,
                    force_page_break=index == 0,
                )
            )

        return blocks

    def _build_available_documents_block(self) -> BlockConfig | None:
        if not self._data.available_documents_html:
            return None

        content = self._data.available_documents_html
        # Split into title (first line) and body (rest)
        lines = content.split("\n", 1)
        title = lines[0] if lines else ""
        body = lines[1] if len(lines) > 1 else ""

        # Build as INFO_TABLE with label (bold title) and value (body)
        # This gives us the bordered container with title-value format
        value_html = f'<span style="white-space: pre-wrap;">{body}</span>'

        # Estimate height
        estimated_lines = len(content) / 120
        estimated_height = int(estimated_lines * 20)
        estimated_height = max(80, estimated_height)

        return BlockConfig(
            type=BlockType.INFO_TABLE,
            estimated_height=estimated_height,
            rows=[[{"label": title, "value": value_html, "width": "100%"}]],
        )

    def _build_excluded_risks_block(self) -> BlockConfig | None:
        if not self._data.excluded_risks_html:
            return None

        content = self._data.excluded_risks_html
        # Estimate height based on content length
        # ~120 chars per line at 14px on 1144px width
        estimated_lines = len(content) / 120
        estimated_height = int(estimated_lines * 20)
        estimated_height = max(100, estimated_height)

        return BlockConfig(
            type=BlockType.TEXT_BLOCK,
            section_header="Riscos Excluídos, Perdas Não Cobertas, Condições Complementares e/ou Condições Particulares",
            estimated_height=estimated_height,
            content=content,
            text_bordered=False,
            text_bold=True,
        )

    def _build_declarations_and_commitments_block(self) -> list[BlockConfig]:
        html_content = self._data.declarations_and_commitments_html_block
        if not html_content:
            return []

        section_title = "DECLARAÇÕES E COMPROMISSOS DO PROPONENTE RELACIONADAS À EXECUÇÃO E CONFORMIDADE CONTRATUAL"
        chunks = self._split_html_into_chunks(html_content, max_chunk_height=1000)
        blocks: list[BlockConfig] = []

        for index, chunk in enumerate(chunks):
            is_last_chunk = index == len(chunks) - 1
            proponent_declaration_data = {"content_html": chunk}

            if is_last_chunk:
                proponent_declaration_data = {
                    "content_html": chunk,
                    "checkbox_checked": True,
                    "checkbox_align": "center",
                    "checkbox_bold": True,
                    "checkbox_text": "Eu me responsabilizo e declaro estar formalmente autorizado e/ou ser o responsável legal, pelo titular destes dados pessoais a fornecê-los a Essor.",
                    "triple_signature": {
                        "left_label": "Local e data:",
                        "center_label": "Assinatura do proponente:",
                        "right_label": "Assinatura do corretor:",
                    },
                }

            blocks.append(
                BlockConfig(
                    type=BlockType.PROPONENT_DECLARATION,
                    section_header=section_title,
                    estimated_height=self._estimate_html_block_height(
                        chunk,
                        minimum=160 if is_last_chunk else 80,
                        extra_padding=120 if is_last_chunk else 0,
                    ),
                    proponent_declaration=proponent_declaration_data,
                )
            )

        return blocks

    def _build_authorization_term_block(self) -> list[BlockConfig]:
        term = self._data.authorization_term
        current_year = date.today().year

        if not term.applicant_name:
            return []

        return [
            BlockConfig(
                type=BlockType.AUTHORIZATION_TERM,
                section_header="Termo Autorização para Pagamento ou Devolução de Crédito por Depósito em Conta Bancária",
                estimated_height=600,
                stops_header_repeat=True,
                force_page_break=True,
                authorization_term={
                    "fields": [
                        {"label": "Nome do proponente", "value": term.applicant_name},
                        {
                            "label": "Número da proposta",
                            "value": self._format_proposal_number(term.proposal_number),
                        },
                        {"label": "Possui conta", "value": term.has_account},
                        {"label": "", "value": term.authorization_text},
                        {"label": "Banco", "value": term.bank_name},
                        {"label": "Nº Agência", "value": term.agency_number},
                        {"label": "Nº da conta", "value": term.account_number or ""},
                        {"label": "Tipo de conta", "value": term.account_type or ""},
                        {"label": "Conta conjunta", "value": term.joint_account or ""},
                    ],
                    "sections": [
                        {"title": "Quitação", "text": term.discharge_text},
                        {
                            "title": "Isenção de responsabilidade",
                            "text": term.liability_text,
                        },
                    ],
                    "closing_text": term.ratification_text,
                    "date_text": f"___________________________________, ________________________________ de {current_year}.",
                    "signature_text": "Assinatura do proponente ou corretor",
                },
            )
        ]

    def _build_authorization_beneficiary_block(self) -> list[BlockConfig]:
        ben = self._data.authorization_beneficiary
        current_year = date.today().year

        if not ben.beneficiary_name:
            return []

        return [
            BlockConfig(
                type=BlockType.AUTHORIZATION_BENEFICIARY,
                section_header="Autorização para pagamento ou devolução de crédito por depósito em conta bancária do beneficiário",
                estimated_height=800,
                force_page_break=True,
                authorization_beneficiary={
                    "initial_fields": [
                        {
                            "label": "Nome do beneficiário",
                            "value": ben.beneficiary_name,
                        },
                        {
                            "label": "Número da proposta",
                            "value": self._format_proposal_number(ben.proposal_number),
                        },
                    ],
                    "authorization_question": ben.authorization_question,
                    "authorization_answer": ben.authorization_answer,
                    "authorization_text": ben.authorization_text,
                    "beneficiary_fields": [
                        {
                            "label": "Nome do beneficiário",
                            "value": ben.beneficiary_full_name,
                        },
                        {
                            "label": "CPF/CNPJ",
                            "value": self._format_cpf_or_cnpj(ben.beneficiary_cpf),
                        },
                        {
                            "label": "Relação do favorecido",
                            "value": ben.beneficiary_relationship,
                        },
                        {"label": "Banco", "value": ben.bank_name, "gap_before": True},
                        {
                            "label": "Nº Agência",
                            "value": ben.agency_number,
                            "gap_before": True,
                        },
                        {
                            "label": "Nº da conta",
                            "value": ben.account_number,
                            "gap_before": True,
                        },                        
                        {
                            "label": "Tipo de conta",
                            "value": ben.account_type,
                            "gap_before": True,
                        },
                        {
                            "label": "Conta conjunta",
                            "value": ben.joint_account,
                            "gap_before": True,
                        },
                        {
                            "label": "Tipo de chave Pix",
                            "value": ben.pix_type,
                            "gap_before": True,
                        },
                        {
                            "label": "Chave Pix",
                            "value": ben.pix_key,
                            "gap_before": True,
                        },
                    ],
                    "observation_text": ben.observation_text,
                    "sections": [
                        {"title": "Quitação", "text": ben.discharge_text},
                        {
                            "title": "Isenção de responsabilidade",
                            "text": ben.liability_text,
                        },
                    ],
                    "closing_text": ben.ratification_text,
                    "date_text": f"_______________________________, _______________________________ de {current_year}.",
                    "signature_text": "Assinatura do segurado",
                    "footer_obs": [
                        "Pessoa física: Reconhecer firma por semelhança.",
                        "Pessoa Jurídica: Reconhecer firma por semelhança e carimbar.",
                    ],
                },
            )
        ]

    def _build_lgpd_consent_block(self) -> list[BlockConfig]:
        lgpd = self._data.lgpd_consent
        if not lgpd.title:
            return []

        signature_text = (
            f"{lgpd.signature_name} / {'CPF' if lgpd.signature_cpf else 'CNPJ'}: "
            f"{self._format_cpf_or_cnpj(lgpd.signature_cpf or lgpd.signature_cnpj)}"
        )

        return [
            BlockConfig(
                type=BlockType.LGPD_CONSENT,
                section_header="Consentimento para Tratamento de Dados Pessoais - LGPD",
                estimated_height=200,
                force_page_break=True,
                stops_header_repeat=True,
                lgpd_consent={
                    "title": lgpd.title,
                    "consent_text": lgpd.consent_text,
                    "signature_text": signature_text,
                },
            )
        ]

    def _build_proponent_declaration_block(self) -> list[BlockConfig]:
        decl = self._data.proponent_declaration
        if not decl.content_html:
            return []

        return [
            BlockConfig(
                type=BlockType.PROPONENT_DECLARATION,
                section_header="DECLARAÇÕES DO CORRETOR DE SEGUROS",
                estimated_height=400,
                force_page_break=True,
                proponent_declaration={
                    "content_html": decl.content_html,
                    "content_bold": decl.content_bold,
                    "checkbox_text": decl.checkbox_text,
                    "checkbox_checked": decl.checkbox_checked,
                    "checkbox_align": decl.checkbox_align,
                    "checkbox_bold": decl.checkbox_bold,
                },
            )
        ]

    def _build_federal_subsidy_term_block(self) -> list[BlockConfig]:
        term = self._data.federal_subsidy_term
        if not term.ministry_header:
            return []

        blocks = [
            BlockConfig(
                type=BlockType.FEDERAL_SUBSIDY_TERM,
                section_header="Subvenção Federal",
                section_header_pagination=True,
                estimated_height=1500,
                federal_subsidy_term={
                    "logo_path": term.logo_path,
                    "ministry_header": term.ministry_header,
                    "committee_text": term.committee_text,
                    "secretariat_text": term.secretariat_text,
                    "main_title": term.main_title,
                    "section_title": term.section_title,
                    "intro_text": term.intro_text,
                    "modality_options": [
                        {"label": m.label, "checked": m.checked}
                        for m in term.modality_options
                    ],
                    "declaration_intro": term.declaration_intro,
                    "declarations": term.declarations,
                    "signature_date_text": term.signature_date_text,
                    "signature_text": term.signature_text,
                    "section2_title": "",
                    "section2_question": "",
                    "section2_options": [],
                    "section2_date_text": "",
                    "section2_responsible_text": "",
                    "section2_cpf_text": "",
                    "section2_signature_text": "",
                },
            )
        ]

        # Bloco da Seção II em página separada
        if term.section2_title:
            blocks.append(
                BlockConfig(
                    type=BlockType.FEDERAL_SUBSIDY_TERM,
                    section_header="Subvenção Federal",
                    section_header_pagination=True,
                    force_page_break=True,
                    estimated_height=400,
                    federal_subsidy_term={
                        "logo_path": term.logo_path,
                        "ministry_header": term.ministry_header,
                        "committee_text": term.committee_text,
                        "secretariat_text": term.secretariat_text,
                        "main_title": term.main_title,
                        "section_title": "",
                        "intro_text": "",
                        "modality_options": [],
                        "declaration_intro": "",
                        "declarations": [],
                        "signature_date_text": "",
                        "signature_text": "",
                        "section2_title": term.section2_title,
                        "section2_question": term.section2_question,
                        "section2_options": term.section2_options,
                        "section2_date_text": term.section2_date_text,
                        "section2_responsible_text": term.section2_responsible_text,
                        "section2_cpf_text": term.section2_cpf_text,
                        "section2_signature_text": term.section2_signature_text,
                    },
                )
            )

        return blocks

    def _build_state_subsidy_term_block(self) -> list[BlockConfig]:
        term = self._data.state_subsidy_term
        if not term.logo_path and not term.government_header:
            return []

        return [
            BlockConfig(
                type=BlockType.STATE_SUBSIDY_TERM,
                section_header="Subvenção Estadual",
                section_header_pagination=True,
                force_page_break=True,
                estimated_height=1200,
                state_subsidy_term={
                    "logo_path": term.logo_path,
                    "government_header": term.government_header,
                    "annex_title": term.annex_title,
                    "intro_text": term.intro_text,
                    "declarations": term.declarations,
                    "date_location_text": term.date_location_text,
                    "signature_text": term.signature_text,
                    "name_cpf_text": term.name_cpf_text,
                },
            )
        ]

    def _build_state_authorization_term_block(self) -> list[BlockConfig]:
        term = self._data.state_authorization_term
        if not term.logo_path and not term.government_header:
            return []

        return [
            BlockConfig(
                type=BlockType.STATE_AUTHORIZATION_TERM,
                section_header="Subvenção Estadual",
                section_header_pagination=True,
                force_page_break=True,
                estimated_height=800,
                state_authorization_term={
                    "logo_path": term.logo_path,
                    "government_header": term.government_header,
                    "government_subheader": term.government_subheader,
                    "annex_title": term.annex_title,
                    "intro_text": term.intro_text,
                    "declarations": term.declarations,
                    "date_location_text": term.date_location_text,
                    "signature_text": term.signature_text,
                    "name_cpf_text": term.name_cpf_text,
                },
            )
        ]

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

    def _format_proposal_number(self, proposal_number: str | None) -> str:
        if not proposal_number:
            return "Não informado"

        digits = "".join(char for char in proposal_number if char.isdigit())
        if len(digits) != 15:
            return proposal_number

        return f"{digits[0]}.{digits[1:4]}.{digits[4:8]}.{digits[8:14]}-{digits[14]}"

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

    def _parse_brl_to_decimal(self, value: str | None) -> Decimal | None:
        if not value:
            return None

        normalized = "".join(ch for ch in value if ch.isdigit() or ch in ",.-")
        if not normalized:
            return None

        if "," in normalized and "." in normalized:
            normalized = normalized.replace(".", "").replace(",", ".")
        elif "," in normalized:
            normalized = normalized.replace(",", ".")

        try:
            return Decimal(normalized)
        except (InvalidOperation, ValueError):
            return None

    def _parse_percentage(self, value: str | None) -> Decimal | None:
        amount = self._parse_brl_to_decimal(value)
        if amount is None:
            return None
        return amount

    def _format_percentage(self, value: str | None) -> str:
        parsed = self._parse_percentage(value)
        if parsed is None:
            return value or ""

        return f"{parsed:.2f}".replace(".", ",") + "%"

    def _get_beneficiary_premium_base(self) -> Decimal | None:
        candidates = [
            self._data.payment.total_premium,
            self._data.payment.net_premium,
            self._data.coverage.applicant_value,
            self._data.coverage.net_premium,
        ]

        for candidate in candidates:
            parsed = self._parse_brl_to_decimal(candidate)
            if parsed is not None:
                return parsed

        return None

    def _calculate_beneficiary_value(
        self,
        premium_amount: Decimal | None,
        percentage: Decimal | None,
    ) -> str:
        if premium_amount is None or percentage is None:
            return "Não informado"

        beneficiary_value = premium_amount * (percentage / Decimal("100"))
        return format_monetary_value(float(beneficiary_value))
