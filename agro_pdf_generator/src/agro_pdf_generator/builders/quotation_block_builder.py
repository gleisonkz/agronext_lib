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

        # Na cotação, não incluímos: subvenção, beneficiários, pessoas autorizadas e observações
        blocks.append(self._build_risk_questionnaire_block())

        # Add information blocks
        blocks.extend(self._build_information_blocks())

        # Add grace period block (after information)
        grace_period = self._build_grace_period_block()
        if grace_period:
            blocks.append(grace_period)

        # Add coverage restrictions block
        coverage_restrictions = self._build_coverage_restrictions_block()
        if coverage_restrictions:
            blocks.append(coverage_restrictions)

        # Add available documents block
        available_documents = self._build_available_documents_block()
        if available_documents:
            blocks.append(available_documents)

        # Add excluded risks block
        excluded_risks = self._build_excluded_risks_block()
        if excluded_risks:
            blocks.append(excluded_risks)

        # Na cotação, não incluímos:
        # - authorization_term (Termo de Autorização para Pagamento)
        # - authorization_beneficiary
        # - lgpd_consent
        # - proponent_declaration
        # - federal_subsidy_term
        # - state_subsidy_term
        # - state_authorization_term

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
                        "value": h.proposal_number,
                        "width": "17%",
                    },
                    {
                        "label": "Data da Cotação",
                        "value": "22/07/2025 - Hora: 11h45",
                        "width": "22%",
                    },
                    {
                        "label": "Versão",
                        "value": "1.0.0 - Data: 22/07/2025 - Hora: 11h45",
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
                    {"label": "CNPJ", "value": h.insurer_cnpj, "width": "25%"},
                    {"label": "SUSEP", "value": h.susep, "width": "25%"},
                    {"label": "Código MAPA", "value": h.mapa_code, "width": "25%"},
                ],
            ],
        )

    def _build_applicant_block(self) -> BlockConfig:
        p = self._data.applicant
        return BlockConfig(
            type=BlockType.INFO_TABLE,
            section_header="Dados Iniciais",
            estimated_height=100,
            rows=[
                [
                    {"label": "Nome/ Razão social", "value": p.name, "width": "25%"},
                    {"label": "CPF", "value": p.cpf, "width": "25%"},
                    {
                        "label": "Data de nascimento",
                        "value": p.birth_date,
                        "width": "25%",
                    },
                    {"label": "Nome social", "value": p.social_name, "width": "25%"},
                ],
                [
                    {"label": "E-mail", "value": p.main_email, "width": "25%"},
                    {"label": "Telefone", "value": p.phone_number, "width": "25%"},
                    {"label": "Tipo", "value": p.phone_type, "width": "25%"},
                    {"label": "WhatsApp", "value": p.is_whatsapp, "width": "25%"},
                ],
            ],
        )

    def _build_address_block(self) -> BlockConfig:
        e = self._data.residential_address
        return BlockConfig(
            type=BlockType.INFO_TABLE,
            section_header="Endereço de Residência",
            estimated_height=120,
            rows=[
                [
                    {"label": "CEP", "value": e.zip_code, "width": "20%"},
                    {"label": "País", "value": e.country, "width": "20%"},
                    {"label": "Estado", "value": e.state, "width": "20%"},
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
                        "label": "LMG/A (R$)",
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
                        "value": c.insured_area_ha,
                        "width": "16%",
                    },
                    {
                        "label": "Quadra/Talhão segurados (qtd)",
                        "value": c.plot_count,
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
                        "value": b.commission_pct,
                        "width": "25%",
                    },
                    {"label": "Telefone", "value": b.phone, "width": "25%"},
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
                        "label": "Tipo de segurado",
                        "value": prop.ownership_type,
                        "width": "25%",
                    },
                    {"label": "Coordenadas", "value": prop.coordinates, "width": "25%"},
                ],
                [
                    {"label": "Cep", "value": prop.zip_code, "width": "20%"},
                    {"label": "País", "value": prop.country, "width": "20%"},
                    {"label": "Estado", "value": prop.state, "width": "20%"},
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

    def _build_risk_questionnaire_block(self) -> BlockConfig:
        rq = self._data.risk_questionnaire

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
            estimated_height=50 + len(rq.questions) * 60,
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

        for i, b in enumerate(self._data.beneficiaries):
            # Row 1: Beneficiário N + Name | CPF | Data de nascimento | Nome social
            rows.append(
                [
                    {
                        "label": f"Beneficiário {i + 1:02d}",
                        "value": b.name,
                        "width": "25%",
                    },
                    {"label": "CPF", "value": b.cpf, "width": "25%"},
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
                    {"label": "Telefone", "value": b.phone, "width": "20%"},
                    {"label": "Porcentagem (%)", "value": b.percentage, "width": "20%"},
                    {"label": "Valor (R$)", "value": b.value, "width": "20%"},
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
                    {"label": "Nome", "value": p.name, "width": "25%"},
                    {"label": "Nome social", "value": p.social_name, "width": "25%"},
                    {"label": "Relação", "value": p.relationship, "width": "25%"},
                    {"label": "Telefone", "value": p.phone, "width": "25%"},
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
        # INFO_TABLE with one row, one column: label "Observações" (bold) and value with text
        # Section header is "Dados Complementares"
        return BlockConfig(
            type=BlockType.INFO_TABLE,
            section_header="Dados Complementares",
            estimated_height=120,
            rows=[
                [
                    {
                        "label": "Observações",
                        "value": self._data.observations,
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
        for i, html_content in enumerate(self._data.information_html_blocks):
            # Estimate height based on content length
            # ~120 chars per line at 16px on 1144px width, ~20px per line
            # Plus 8px margin between paragraphs
            estimated_lines = len(html_content) / 120
            estimated_height = int(
                estimated_lines * 20 + html_content.count("</p>") * 8
            )
            # Minimum height of 50px, no maximum cap to allow proper page breaks
            estimated_height = max(50, estimated_height)

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
            section_header="Riscos Excluídos, Perdas Não Cobertas e/ou Condições Particulares",
            estimated_height=estimated_height,
            content=content,
            text_bordered=False,
            text_bold=True,
        )

    def _build_authorization_term_block(self) -> list[BlockConfig]:
        term = self._data.authorization_term
        if not term.applicant_name:
            return []

        return [
            BlockConfig(
                type=BlockType.AUTHORIZATION_TERM,
                section_header="Termo de Autorização para Pagamento ou Devolução de Crédito por Depósito em Conta Bancária",
                estimated_height=600,
                authorization_term={
                    "fields": [
                        {"label": "Nome do proponente", "value": term.applicant_name},
                        {"label": "Número da proposta", "value": term.proposal_number},
                        {"label": "Possui conta", "value": term.has_account},
                        {"label": "Banco", "value": term.bank_name},
                        {"label": "Nº Agência", "value": term.agency_number},
                        {"label": "Dígito", "value": term.agency_digit, "inline": True},
                        {"label": "Nº da conta", "value": term.account_number},
                        {
                            "label": "Dígito",
                            "value": term.account_digit,
                            "inline": True,
                        },
                        {"label": "Tipo de conta", "value": term.account_type},
                        {"label": "Conta conjunta", "value": term.joint_account},
                    ],
                    "intro_text": term.authorization_text,
                    "sections": [
                        {"title": "Quitação", "text": term.discharge_text},
                        {
                            "title": "Isenção de responsabilidade",
                            "text": term.liability_text,
                        },
                    ],
                    "closing_text": term.ratification_text,
                    "date_text": "_________________________, _________________________ de 2025.",
                    "signature_text": "Assinatura do proponente ou corretor",
                },
            )
        ]

    def _build_authorization_beneficiary_block(self) -> list[BlockConfig]:
        ben = self._data.authorization_beneficiary
        if not ben.beneficiary_name:
            return []

        return [
            BlockConfig(
                type=BlockType.AUTHORIZATION_BENEFICIARY,
                section_header="Autorização para pagamento ou devolução de crédito por depósito em conta bancária do beneficiário",
                estimated_height=800,
                authorization_beneficiary={
                    "initial_fields": [
                        {
                            "label": "Nome do beneficiário",
                            "value": ben.beneficiary_name,
                        },
                        {"label": "Número da proposta", "value": ben.proposal_number},
                    ],
                    "authorization_question": ben.authorization_question,
                    "authorization_answer": ben.authorization_answer,
                    "authorization_text": ben.authorization_text,
                    "beneficiary_fields": [
                        {
                            "label": "Nome do beneficiário",
                            "value": ben.beneficiary_full_name,
                        },
                        {"label": "CPF", "value": ben.beneficiary_cpf},
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
                        {"label": "Dígito", "value": ben.agency_digit, "inline": True},
                        {
                            "label": "Nº da conta",
                            "value": ben.account_number,
                            "gap_before": True,
                        },
                        {"label": "Dígito", "value": ben.account_digit, "inline": True},
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
                    "date_text": "_________________________, _________________________ de 2025.",
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

        signature_text = f"{lgpd.signature_name} / CPF: {lgpd.signature_cpf}"

        return [
            BlockConfig(
                type=BlockType.LGPD_CONSENT,
                section_header="Consentimento para Tratamento de Dados Pessoais - LGPD",
                estimated_height=200,
                force_page_break=True,
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
                section_header="Declaração do Proponente",
                estimated_height=400,
                stops_header_repeat=True,  # Para de repetir header/logo após este bloco
                proponent_declaration={
                    "content_html": decl.content_html,
                    "content_bold": decl.content_bold,
                    "checkbox_text": decl.checkbox_text,
                    "checkbox_checked": decl.checkbox_checked,
                    "checkbox_align": decl.checkbox_align,
                    "checkbox_bold": decl.checkbox_bold,
                    "triple_signature": {
                        "left_label": decl.left_label,
                        "center_label": decl.center_label,
                        "right_label": decl.right_label,
                    },
                    "observation_text": decl.observation_text,
                    "footer_bordered_text": decl.footer_bordered_text,
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
        if not term.government_header:
            return []

        return [
            BlockConfig(
                type=BlockType.STATE_SUBSIDY_TERM,
                section_header="Subvenção Estadual",
                section_header_pagination=True,
                force_page_break=True,
                estimated_height=1200,
                state_subsidy_term={
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
