from ..blocks import BlockConfig, BlockType
from ..config import Spacing
from ..schemas import SimulationPdfData


class SimulationBlockBuilder:
    def __init__(self, data: SimulationPdfData):
        self._data = data

    def build_all(self) -> list[BlockConfig]:
        blocks = [
            self._build_logo_block(),
            self._build_title_block(),
            self._build_header_block(),
            self._build_proponent_block(),
            self._build_location_block(),
            self._build_productivity_block(),
            self._build_results_block(),
            self._build_broker_block(),
            self._build_general_info_block(),
        ]
        return [block for block in blocks if block is not None]

    def _build_logo_block(self) -> BlockConfig:
        return BlockConfig(
            type=BlockType.LOGO,
            estimated_height=70,
            repeat_on_pages=True,
            keep_space_when_hidden=True,
            logo_path=self._data.header.logo_path,
        )

    def _build_title_block(self) -> BlockConfig:
        return BlockConfig(
            type=BlockType.HTML_BLOCK,
            estimated_height=30,
            content=(
                '<div style="text-align: center; font-weight: 600; '
                'font-size: 16px; margin-bottom: 8px;">'
                'SIMULAÇÃO DE SEGURO'
                "</div>"
            ),
        )

    def _build_header_block(self) -> BlockConfig:
        h = self._data.header
        return BlockConfig(
            type=BlockType.INFO_TABLE,
            estimated_height=150,
            rows=[
                [
                    {
                        "label": "Data da simulação de seguro",
                        "value": h.simulation_date,
                        "width": "50%",
                    },
                    {
                        "value": h.simulation_status,
                        "width": "50%",
                        "background_color": "#FEF2F2",
                        "text_color": "#B91C1C",
                    },
                ],
                [
                    {"label": "Cultura", "value": h.crop, "width": "15%"},
                    {
                        "label": "Cobertura Principal",
                        "value": h.main_coverage,
                        "width": "35%",
                    },
                    {"label": "Safra", "value": h.harvest, "width": "20%"},
                    {"label": "BACEN", "value": h.bacen_code, "width": "30%"},
                ],
                [
                    {"label": "Seguradora", "value": h.insurer, "width": "25%"},
                    {"label": "CNPJ", "value": h.insurer_cnpj, "width": "25%"},
                    {"label": "SUSEP", "value": h.susep, "width": "25%"},
                    {"label": "Código MAPA", "value": h.mapa_code, "width": "25%"},
                ],
            ],
        )

    def _build_proponent_block(self) -> BlockConfig:
        p = self._data.proponent
        return BlockConfig(
            type=BlockType.INFO_TABLE,
            section_header="Dados do Proponente",
            estimated_height=80,
            rows=[
                [
                    {"label": "Nome", "value": p.name, "width": "50%"},
                    {"label": "Telefone", "value": p.phone, "width": "50%"},
                ]
            ],
        )

    def _build_location_block(self) -> BlockConfig:
        loc = self._data.location
        return BlockConfig(
            type=BlockType.INFO_TABLE,
            section_header="Localidade",
            estimated_height=80,
            rows=[
                [
                    {"label": "Estado", "value": loc.state, "width": "25%"},
                    {"label": "Município", "value": loc.city, "width": "25%"},
                    {"label": "País", "value": loc.country, "width": "25%"},
                    {
                        "label": "Coordenadas",
                        "value": loc.coordinates,
                        "width": "25%",
                    },
                ]
            ],
        )

    def _build_productivity_block(self) -> BlockConfig:
        prod = self._data.productivity
        return BlockConfig(
            type=BlockType.INFO_TABLE,
            section_header="Produtividade",
            estimated_height=120,
            row_gap_after=[0],
            rows=[
                [
                    {"label": "Franquia (%)", "value": prod.deductible_pct, "width": "25%"},
                    {"label": "Área (ha)", "value": prod.area_ha, "width": "25%"},
                    {
                        "label": "Produtividade (ton/ha)",
                        "value": prod.productivity_ton_ha,
                        "width": "25%",
                    },
                    {
                        "label": "Valor da tonelada (R$)",
                        "value": prod.price_per_ton_brl,
                        "width": "25%",
                    },
                ],
                [
                    {
                        "label": "LMGA (Importância segurada - R$)",
                        "value": prod.lmga_brl,
                        "width": "40%",
                    },
                    {
                        "label": "Prêmio tarifário (R$)",
                        "value": prod.tariff_premium_brl,
                        "width": "30%",
                    },
                    {"label": "Taxa (%)", "value": prod.rate_pct, "width": "30%"},
                ],
            ],
        )

    def _build_results_block(self) -> BlockConfig:
        r = self._data.results
        return BlockConfig(
            type=BlockType.INFO_TABLE,
            section_header="Resultado da Simulação",
            estimated_height=240,
            rows=[
                [
                    {
                        "label": "Prêmio Líquido aproximado (R$)",
                        "value": r.net_premium_brl,
                        "width": "100%",
                    }
                ],
                [
                    {
                        "label": "Subvenção federal (%)",
                        "value": r.federal_subsidy_pct,
                        "width": "50%",
                    },
                    {
                        "label": "Valor subvenção federal aproximado (R$)",
                        "value": r.federal_subsidy_brl,
                        "width": "50%",
                    },
                ],
                [
                    {
                        "label": "Valor proponente com apenas subvenção federal aproximado (R$)",
                        "value": r.value_with_only_federal_brl,
                        "width": "100%",
                    }
                ],
                [
                    {
                        "label": "Subvenção estadual (%)",
                        "value": r.state_subsidy_pct,
                        "width": "50%",
                    },
                    {
                        "label": "Valor subvenção estadual aproximado (R$)",
                        "value": r.state_subsidy_brl,
                        "width": "50%",
                    },
                ],
                [
                    {
                        "label": "Valor proponente com apenas subvenção estadual aproximado (R$)",
                        "value": r.value_with_only_state_brl,
                        "width": "100%",
                    }
                ],
                [
                    {
                        "label": "Valor proponente aproximado (R$)",
                        "value": r.applicant_value_brl,
                        "width": "100%",
                    }
                ],
            ],
        )

    def _build_broker_block(self) -> BlockConfig:
        b = self._data.broker
        emails = self._format_list_items(b.emails)
        phones = self._format_list_items(b.phones)

        return BlockConfig(
            type=BlockType.INFO_TABLE,
            section_header="Corretora",
            estimated_height=120,
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
                    {"label": "Telefone", "value": b.phone, "width": "25%"},
                ],
                [
                    {"label": "E-mail", "value": emails, "width": "50%"},
                    {"label": "Telefone", "value": phones, "width": "50%"},
                ],
            ],
        )

    def _build_general_info_block(self) -> BlockConfig | None:
        if not self._data.general_info_html:
            return None
        return BlockConfig(
            type=BlockType.HTML_BLOCK,
            section_header="INFORMAÇÕES GERAIS",
            estimated_height=180,
            content=self._data.general_info_html,
        )

    def _format_list_items(self, items: list[str]) -> str:
        return "".join(
            f'<div style="margin-bottom: {Spacing.MD};">{item}</div>'
            if i < len(items) - 1
            else f"<div>{item}</div>"
            for i, item in enumerate(items)
        )
