from enum import Enum
from typing import TypedDict

from agro_pdf_generator.base_model import BaseModel, Field


class BlockType(str, Enum):
    LOGO = "logo"
    INFO_TABLE = "info_table"
    DATA_TABLE = "data_table"
    TEXT_BLOCK = "text_block"
    HTML_BLOCK = "html_block"
    IMAGE = "image"
    CHECKBOX = "checkbox"
    SIGNATURE = "signature"
    AUTHORIZATION_TERM = "authorization_term"
    DATE_LINE = "date_line"
    SIGNATURE_LINE = "signature_line"
    DATE_LOCATION_LINE = "date_location_line"
    AUTHORIZATION_BENEFICIARY = "authorization_beneficiary"
    LGPD_CONSENT = "lgpd_consent"
    PROPONENT_DECLARATION = "proponent_declaration"
    FEDERAL_SUBSIDY_TERM = "federal_subsidy_term"
    STATE_SUBSIDY_TERM = "state_subsidy_term"
    STATE_AUTHORIZATION_TERM = "state_authorization_term"


class LabelValueItem(TypedDict, total=False):
    label: str
    value: str
    inline: bool  # Se True, continua na mesma linha do anterior
    gap_before: bool  # Se True, adiciona espaço maior antes deste field


class TitleTextItem(TypedDict, total=False):
    title: str
    text: str


class AuthorizationTermConfig(TypedDict, total=False):
    fields: list[LabelValueItem]  # Nome, Banco, Agência, etc.
    intro_text: str  # Texto de autorização antes dos dados bancários
    sections: list[TitleTextItem]  # Quitação, Isenção, etc.
    closing_text: str  # Texto centralizado antes da data (Firmo...)
    date_text: str  # Linha de data (usa DATE_LINE internamente)
    signature_text: str  # Texto da assinatura (usa SIGNATURE_LINE internamente)


class AuthorizationBeneficiaryConfig(TypedDict, total=False):
    header_title: str  # Título no box do header
    initial_fields: list[LabelValueItem]  # Nome do beneficiário, Número da proposta
    authorization_question: str  # Pergunta do checkbox
    authorization_answer: str  # Resposta (Sim/Não)
    authorization_text: str  # Texto de autorização após checkbox
    beneficiary_fields: list[LabelValueItem]  # Dados do beneficiário (Nome, CPF, Banco, etc.)
    observation_text: str  # Texto em itálico após os campos
    sections: list[TitleTextItem]  # Quitação, Isenção, etc.
    closing_text: str  # Texto centralizado (Firmo...)
    date_text: str  # Linha de data
    signature_text: str  # Texto da assinatura
    footer_obs: list[str]  # Lista de OBS no final


class LgpdConsentConfig(TypedDict, total=False):
    title: str  # Título centralizado (ex: SEGURADO)
    consent_text: str  # Texto de consentimento centralizado
    signature_text: str  # Texto da assinatura (ex: João da Silva / CPF: 000.000.000-00)


class TripleSignatureConfig(TypedDict, total=False):
    left_label: str  # Ex: "Local e data:"
    center_label: str  # Ex: "Assinatura do proponente:"
    right_label: str  # Ex: "Assinatura do corretor:"


class ProponentDeclarationConfig(TypedDict, total=False):
    content_html: str  # Conteúdo HTML principal
    content_bold: bool  # Se True, todo o conteúdo HTML fica em negrito
    checkbox_text: str  # Texto do checkbox (se vazio, não mostra checkbox)
    checkbox_checked: bool  # Se o checkbox está marcado
    checkbox_align: str  # "top" ou "center" - alinhamento do checkbox com o texto
    checkbox_bold: bool  # Se True, texto do checkbox fica em negrito
    triple_signature: TripleSignatureConfig  # Assinaturas em 3 colunas
    observation_text: str  # Texto pequeno de observação
    footer_bordered_text: str  # Texto com borda no final


class FederalSubsidyTermConfig(TypedDict, total=False):
    ministry_header: str  # Título do ministério
    committee_text: str  # Comitê Gestor
    secretariat_text: str  # Secretaria-Executiva
    main_title: str  # Título principal do termo
    section_title: str  # Título da seção (SEÇÃO I)
    intro_text: str  # Texto introdutório
    modality_options: list[dict]  # Lista de modalidades com checkbox
    declaration_intro: str  # Texto antes das declarações
    declarations: list[str]  # Lista de declarações (a, b, c, etc.)
    signature_date_text: str  # Texto de data
    signature_text: str  # Texto de assinatura
    # Seção II
    section2_title: str  # Título da SEÇÃO II
    section2_question: str  # Pergunta da SEÇÃO II
    section2_options: list[str]  # Opções de resposta
    section2_date_text: str  # Data
    section2_responsible_text: str  # Dados do responsável
    section2_cpf_text: str  # CPF
    section2_signature_text: str  # Assinatura


class StateSubsidyTermConfig(TypedDict, total=False):
    government_header: str  # Ex: "GOVERNO DO ESTADO DO PARANÁ..."
    annex_title: str  # Ex: "ANEXO III - TERMO DE RESPONSABILIDADE"
    intro_text: str  # Texto introdutório com dados do produtor
    declarations: list[str]  # Lista de declarações (I, II, III, etc.)
    date_location_text: str  # Texto com campos de data e local
    signature_text: str  # Texto de assinatura
    name_cpf_text: str  # Nome e CPF do produtor


class StateAuthorizationTermConfig(TypedDict, total=False):
    logo_path: str  # Caminho para a logo do estado
    government_header: str  # Ex: "GOVERNO DO ESTADO"
    government_subheader: str  # Ex: "SECRETARIA DA AGRICULTURA E DO ABASTECIMENTO"
    annex_title: str  # Ex: "ANEXO IV - TERMO DE AUTORIZAÇÃO"
    intro_text: str  # Texto introdutório com dados do produtor
    declarations: list[str]  # Lista de declarações (I, II, etc.)
    date_location_text: str  # Data e local formatado
    signature_text: str  # Texto de assinatura
    name_cpf_text: str  # Nome e CPF do produtor


class DataTableVariant(str, Enum):
    DEFAULT = "default"
    CENTERED_UPPERCASE = "centered_uppercase"
    CENTERED_NORMAL = "centered_normal"
    SMALL_CENTERED_UPPERCASE = "small_centered_uppercase"
    SMALL_CENTERED_NORMAL = "small_centered_normal"


class CheckboxAlign(str, Enum):
    TOP = "top"
    CENTER = "center"


class CellConfig(TypedDict, total=False):
    label: str
    value: str
    width: str
    background_color: str
    text_color: str


class CheckboxItem(TypedDict, total=False):
    label: str
    checked: bool


class SignatureConfig(TypedDict, total=False):
    title: str
    name: str


class BlockConfig(BaseModel):
    model_config = {"frozen": False}

    type: BlockType
    section_header: str | None = None
    section_second_header: str | None = None
    section_header_pagination: bool = False  # Se True, mostra paginação no section header
    estimated_height: int = 100
    repeat_on_pages: bool = False  # Se True, repete em todas as páginas
    repeat_on_page_range: str | None = None  # Range de páginas ex: "1-9", "2-5"
    force_page_break: bool = False  # Se True, força quebra de página antes deste bloco
    stops_header_repeat: bool = False  # Se True, para de repetir headers após este bloco
    keep_space_when_hidden: bool = False  # Se True, mantém espaço mesmo quando hidden

    # INFO_TABLE
    rows: list[list[CellConfig]] = Field(default_factory=list)
    no_margin: bool = False
    row_gap_after: list[int] = Field(default_factory=list)  # Row indices after which to add gap

    # DATA_TABLE
    headers: list[str] = Field(default_factory=list)
    data_rows: list[list[str]] = Field(default_factory=list)
    widths: list[str] = Field(default_factory=list)
    variant: DataTableVariant = DataTableVariant.DEFAULT

    # TEXT_BLOCK / HTML_BLOCK
    content: str = ""
    text_bordered: bool = True
    text_bold: bool = False

    # LOGO
    logo_path: str = ""

    # IMAGE
    image_path: str = ""
    image_bytes: bytes = b""  # raw bytes; renderer will base64 encode when present
    image_max_height: str = "400px"

    # CHECKBOX
    checkbox_items: list[CheckboxItem] = Field(default_factory=list)
    checkbox_align: CheckboxAlign = CheckboxAlign.TOP

    # SIGNATURE
    signatures: list[SignatureConfig] = Field(default_factory=list)
    date_location: str = ""

    # AUTHORIZATION_TERM
    authorization_term: AuthorizationTermConfig | None = None

    # DATE_LINE
    date_text: str = ""

    # SIGNATURE_LINE
    signature_text: str = ""

    # DATE_LOCATION_LINE
    date_location_label: str = ""  # Ex: "Local e data"

    # AUTHORIZATION_BENEFICIARY
    authorization_beneficiary: AuthorizationBeneficiaryConfig | None = None

    # LGPD_CONSENT
    lgpd_consent: LgpdConsentConfig | None = None

    # PROPONENT_DECLARATION
    proponent_declaration: ProponentDeclarationConfig | None = None

    # FEDERAL_SUBSIDY_TERM
    federal_subsidy_term: FederalSubsidyTermConfig | None = None

    # STATE_SUBSIDY_TERM
    state_subsidy_term: StateSubsidyTermConfig | None = None

    # STATE_AUTHORIZATION_TERM
    state_authorization_term: StateAuthorizationTermConfig | None = None
