from datetime import date
from enum import IntEnum, StrEnum
from typing import Optional

from plug_sdk.base_model import BaseModel, Field, computed_field

LOCATION_CODE = 4
PAYMENT_METHOD_CODE: int = 16
BILLING_MODE_CODE: int = 1
DEDUCTIBLE_TABLE_CODE: int = 100
CLAUSE_CODE: int = 100


class GeographicPositions(StrEnum):
    NORTH = "N"
    SOUTH = "S"
    EAST = "E"
    WEST = "W"


class EndorsementCode(IntEnum):
    CANCELLATION = 2
    REFUND = 3
    NO_MOVEMENT = 4
    BILLING = 6


class PartyType(IntEnum):
    NATURAL_PERSON = 1
    LEGAL_ENTITY = 2


class UsageTypes(StrEnum):
    RESIDENTIAL = "Residencial"


class QuestionnaireResponseTypes(StrEnum):
    ALPHANUMERIC = "Alfanumerico"


class ItemTypes(StrEnum):
    AGRICULTURAL = "Agricola"


class DeductibleTableType(StrEnum):
    FQ = "FQ"  # Fixed Deductible


class TermTypes(IntEnum):
    CLOSED = 1  # Fixed Term
    OPEN = 2  # Renewable Term


class ComissionCodeType(IntEnum):
    AGENCY = 1
    BROKERAGE = 2
    PROLABORE = 3


class PolicyTypes(IntEnum):
    INDIVIDUAL = 2
    COLLECTIVE = 4


class CommunicationMethodTypes(IntEnum):
    PHONE = 2
    CELL = 3
    EMAIL = 4


class DocumentTypes(StrEnum):
    RG = "RG"


class PartyRoleCode(IntEnum):
    BROKER = 1
    CLIENT = 2
    POLICYHOLDER = 3
    BENEFICIARY = 4
    SERVICE_PROVIDER = 5
    PRODUCER = 6
    PEER_COMPANY = 7
    SUB_POLICYHOLDER = 8
    REINSURER = 9
    OTHERS = 10
    ATTORNEY_IN_FACT = 12
    POLICY_TAKER = 14
    INSPECTOR = 15
    ATTENDING_PHYSICIAN = 16
    SHAREHOLDER = 17
    SPOUSE = 19
    CONTACT = 20
    EMPLOYEE = 21
    DRIVER = 22
    THIRD_PARTY = 23
    GUARANTOR = 24
    SUPPLIER = 25
    LEGAL_REPRESENTATIVE = 26
    INSURANCE_BROKER = 27
    CLAIMANT = 32
    FEDERAL_AGENCY = 33
    STATE_AGENCY = 34
    PARTNER = 51
    PROPERTY_RESPONSIBLE = 52
    SURVEYOR = 53
    EXPERT = 54
    INSURER = 55
    PARTICIPANT = 58
    ACCOUNT_MANAGER = 59
    PAYEE = 67
    PARTNER_OWNER = 69
    ADVISORY = 83
    INTERMEDIARY = 113


class AnswerCodes(IntEnum):
    YES_OR_CUSTOM = 1
    NO = 2


class QuestionCodes(IntEnum):
    FEDERAL_SUBSIDY = 101
    STATE_SUBSIDY = 108
    FULL_CULTIVATED_AREA = 103
    PRE_EXISTING_DAMAGE = 109
    ANOTHER_PLOT_SAME_CROP = 106
    ANOTHER_INSURANCE = 107


### === SUBVENÇÃO === ###


class Subsidy(BaseModel):
    is_federal: bool = Field(alias="indicadorSubvencaoFederal")
    federal_value: float = Field(alias="valorSubvencaoFederal")
    is_state: bool = Field(alias="indicadorSubvencaoEstadual")
    state_value: float = Field(alias="valorSubvencaoEstadual")
    is_suspended: bool = Field(alias="indicadorSubvencaoSuspensa", default=False)
    is_deferred: bool = Field(alias="indicadorAdiada", default=False)


### === VIGÊNCIA === ###


class BaseInsuranceTerm(BaseModel):
    start_date: date = Field(alias="dataInicio")
    end_date: date = Field(alias="dataFim")


class InsuranceTerm(BaseInsuranceTerm):
    term_type: TermTypes = Field(alias="tipoVigencia", default=TermTypes.CLOSED)


class ItemTerm(BaseInsuranceTerm):
    term_type: TermTypes = Field(alias="tipo", default=TermTypes.CLOSED)


### === COMISSIONAMENTO === ###


class CommissionParticipant(BaseModel):
    name: str = Field(alias="nome")
    is_leader: int = Field(alias="lider", default=1)
    party_type: PartyType = Field(alias="tipoPessoa")
    document: str = Field(alias="cpfCnpj")
    participation_percentage: float = Field(alias="percentualParticipacao", default=100.0)
    commission_type_code: ComissionCodeType = Field(alias="codigoTipoComissao", default=ComissionCodeType.BROKERAGE)
    inspector_code: int = Field(alias="codigoInspetor", default=1854)  # TODO: Check if this is always 1854


class CommissionRules(BaseModel):
    percentage: float = Field(alias="percentual")
    commission_coefficient: float = Field(alias="coeficienteComissao", default=0.0)
    participants: list[CommissionParticipant] = Field(alias="participantes", default_factory=list)


### === COBRANÇA === ###


class BaseFinancialInfo(BaseModel):
    net_value: float = Field(alias="valorLiquido")
    total_value: float = Field(alias="valorTotal")
    tariff_value: float = Field(alias="valorTarifario")
    # TODO: Check if below is always 0.0 and why
    discount_percentage: float = Field(alias="percentualDesconto", default=0.0)
    surcharge_percentage: float = Field(alias="percentualAgravamento", default=0.0)
    discount_value: float = Field(alias="valorDesconto", default=0.0)
    surcharge_value: float = Field(alias="valorAgravamento", default=0.0)
    load_percentage: float = Field(alias="percentualCarregamento")


class ExtendedFinancialInfo(BaseFinancialInfo):
    iof_value: float = Field(alias="valorIof", default=0.0)
    interest_value: float = Field(alias="valorJuros", default=0.0)
    policy_cost_value: float = Field(alias="valorCustoApolice", default=0.0)
    iof_percentage: float = Field(alias="percentualIof", default=0.0)
    inspection_cost_value: float = Field(alias="valorCustoVistoria", default=0.0)
    interest_percentage: float = Field(alias="percentualJuros", default=0.0)


class Premium(ExtendedFinancialInfo):
    pass  # Inherits all fields as-is


class Installment(ExtendedFinancialInfo):
    installment_number: int = Field(alias="numeroParcela")
    due_date: date = Field(alias="dataVencimento")
    state_subsidy_value: float = Field(alias="valorSubvencaoEstadual")
    federal_subsidy_value: float = Field(alias="valorSubvencaoFederal")
    insured_value: float = Field(alias="valorSegurado")


class Billing(BaseModel):
    installment_plan_id: Optional[int] = Field(alias="idParcelamento", default=None)
    payment_method_code: int = Field(
        alias="codigoFormaPagamento",
        default=PAYMENT_METHOD_CODE,
    )
    billing_mode_code: int = Field(
        alias="codigoModalidadeCobranca",
        default=BILLING_MODE_CODE,
    )
    billing_day_number: Optional[int] = Field(alias="numeroDiaCobranca", default=None)
    installments: list[Installment] = Field(alias="parcelas", default_factory=list)


### === ITEM === ###


class ClausePremium(BaseFinancialInfo):
    commercial_rate: float = Field(alias="taxaComercial")
    # pure_rate: float = Field(alias="taxaPura")

    @computed_field(alias="taxaPura")
    @property
    def pure_rate(self) -> float:
        return self.commercial_rate


class InsuredAmount(BaseModel):
    value: float = Field(alias="valor")
    rate: float = Field(alias="taxa")


class DeductibleTable(BaseModel):
    code: int = Field(alias="codigo", default=DEDUCTIBLE_TABLE_CODE)
    type: DeductibleTableType = Field(alias="tipo", default=DeductibleTableType.FQ)


class Deductible(BaseModel):
    value: float = Field(alias="valor")
    code: int = Field(alias="codigo", default=DEDUCTIBLE_TABLE_CODE)
    table: Optional[DeductibleTable] = Field(alias="tabela", default=None)


class Clause(BaseModel):
    code: int = Field(alias="codigo", default=CLAUSE_CODE)
    is_contracted: bool = Field(alias="isContratada", default=True)
    deductible: Deductible = Field(alias="franquia")
    insured_amount: InsuredAmount = Field(alias="importanciaSegurada")
    premium: ClausePremium = Field(alias="premio")


class Coverage(BaseModel):
    code: int = Field(alias="codigo")
    is_additional: bool = Field(alias="indicadorFacultativa")
    is_free: bool = Field(alias="indicadorGratuita", default=False)
    base_premium_value: float = Field(alias="valorPremioBasico", default=0.0)
    clauses: list[Clause] = Field(alias="verbas")


class Variety(BaseModel):
    name: str = Field(alias="nome")
    code: int = Field(alias="codigo")
    cycle_code: int = Field(alias="codigoCiclo")


class Crop(BaseModel):
    code: str = Field(alias="codigo")
    name: str = Field(alias="nome")
    sub_crop_code: int = Field(alias="codigoSubCultura")
    variety: Variety = Field(alias="variedade")


class Polygon(BaseModel):
    number: int = Field(alias="numero")


class CoordinateEntry(BaseModel):
    degree_latitude: int = Field(alias="numeroGrauLatitude")
    minute_latitude: int = Field(alias="numeroMinutoLatitude")
    second_latitude: float = Field(alias="numeroSegundoLatitude")
    orientation_latitude: str = Field(alias="csOrientacaoLatitude")
    degree_longitude: int = Field(alias="numeroGrauLongitude")
    minute_longitude: int = Field(alias="numeroMinutoLongitude")
    second_longitude: float = Field(alias="numeroSegundoLongitude")
    orientation_longitude: str = Field(alias="csOrientacaoLongitude")


class CoordinatesList(BaseModel):
    polygon: Polygon = Field(alias="poligonos")
    coordinates: list[CoordinateEntry] = Field(alias="coordenadas")


class Item(BaseModel):
    type: ItemTypes = Field(alias="tipo", default=ItemTypes.AGRICULTURAL)
    crop: Crop = Field(alias="cultura")
    coverages: list[Coverage] = Field(alias="coberturas")
    term: InsuranceTerm = Field(alias="vigencia")
    coordinates_list: CoordinatesList = Field(alias="listaCoordenadas")
    productivity: float = Field(alias="produtividadeGarantida")
    plot_index: int = Field(alias="codigo")
    area: float = Field(alias="area")
    ton_value: float = Field(alias="valorTonelada")
    ##
    ton_yield_value: float = Field(alias="valorRendimentoTonelada")  # TODO: Equal to ton_value? Why?
    estimated_yield_value: float = Field(alias="valorRendimentoEstimado", default=3)  # TODO: It makes no sense to be 3 Why?
    crop_ton_value: float = Field(alias="valorToneladaCultura")  # TODO: Equal to ton_value? Why?
    ##
    description: Optional[str] = Field(alias="descricao", default=None)
    has_coverage: bool = Field(alias="indicadorCobertura", default=True)  # TODO: Check if this is always True Why?
    sowing_date: Optional[date] = Field(alias="dataSemeadura", default=None)  # TODO: Check if this is always None Why?
    paf_value: Optional[float] = Field(alias="valorPaf", default=None)  # TODO: Check if this is always None Why?
    insured_value_per_ha: float = Field(alias="valorSeguradoHa", default=0.0)  # TODO: Check if this is always 0.0 Why?
    age: int = Field(alias="idade", default=0)  # TODO: Check if this is always 0 Why?
    guaranteed_fruit_number: int = Field(alias="numeroFrutoGarantido", default=0)  # TODO: Check if this is always 0 Why?
    spacing: str = Field(alias="espacamento", default_factory=lambda: "X")  # TODO: dont even know where to start


### === QUESTIONARIO === ###


class Answer(BaseModel):
    score: int = Field(alias="pontuacao", default=0)
    justification: Optional[str] = Field(alias="justificativa", default=None)
    description: Optional[str] = Field(alias="descricao", default=None)
    code: int = Field(alias="codigo")


class Question(BaseModel):
    code: int = Field(alias="codigo")
    question_text: str = Field(alias="descricao")
    answers: list[Answer] = Field(alias="resposta")


class Questionnaire(BaseModel):
    coefficient: float = Field(alias="coeficiente", default=0.0)
    answer_type: QuestionnaireResponseTypes = Field(alias="tipoResposta", default=QuestionnaireResponseTypes.ALPHANUMERIC)
    questions: list[Question] = Field(alias="perguntas")


### === LOCAL === ###


class AddressData(BaseModel):
    postal_code: int = Field(alias="cep")
    street: str = Field(alias="logradouro")
    neighborhood: str = Field(alias="bairro")
    city: str = Field(alias="municipio")
    state: str = Field(alias="estado")
    state_abbreviation: str = Field(alias="uf")
    state_code: int = Field(alias="codigoUf")
    complement: str = Field(alias="complemento")
    bacen_city_code: Optional[str] = Field(alias="codigoBacenMunicipio")


class Coordinate(BaseModel):
    degree: int = Field(alias="grau")
    minute: int = Field(alias="minuto")
    second: float = Field(alias="segundo")
    position: GeographicPositions = Field(alias="posicao")


class Geo(BaseModel):
    latitude: Coordinate = Field(alias="latidude")
    longitude: Coordinate = Field(alias="longitude")


class Location(BaseModel):
    code: int = Field(alias="codigo", default=LOCATION_CODE)
    usage: UsageTypes = Field(alias="utilizacao", default=UsageTypes.RESIDENTIAL)
    name: str = Field(alias="nome")
    number: int = Field(alias="numero")
    deductible_value: float = Field(alias="valorFranquia")
    address: AddressData = Field(alias="endereco")
    questionnaire: Questionnaire = Field(alias="questionario")
    geo: Geo = Field(alias="geo")
    items: list[Item] = Field(alias="itens")


### === PESSOAS === ###


class IdentificationDocument(BaseModel):
    number: int = Field(alias="numero")
    issuing_agency: str = Field(alias="orgaoExpedidor")
    issue_date: str = Field(alias="dataExpedicao")
    state: str = Field(alias="uf")
    document_type: DocumentTypes = Field(alias="tipo", default=DocumentTypes.RG)


class PartyDetails(BaseModel):
    is_own_cpf: Optional[bool] = Field(alias="isCpfProprio", default=None)
    trade_name: Optional[str] = Field(alias="nomeFantasia", default=None)
    birth_date: Optional[date] = Field(alias="dataNascimento", default=None)
    gender: Optional[str] = Field(alias="genero", default=None)
    marital_status: Optional[str] = Field(alias="estadoCivil", default=None)
    identification_document: Optional[list[IdentificationDocument]] = Field(alias="documentoIdentificacao", default_factory=list)


class PartyRole(BaseModel):
    role_code: PartyRoleCode = Field(alias="codigoPapel")
    # role_description: PartyRoleDescription = Field(alias="descricaoPapel")
    participation_percentage: Optional[float] = Field(alias="percentualParticipacao", default=None)

    @computed_field(alias="descricaoPapel")
    @property
    def description(self) -> str:  # noqa: C901
        match self.role_code:
            case PartyRoleCode.BROKER:
                return "Corretor"
            case PartyRoleCode.CLIENT:
                return "Cliente"
            case PartyRoleCode.POLICYHOLDER:
                return "Segurado"
            case PartyRoleCode.BENEFICIARY:
                return "Beneficiário"
            case PartyRoleCode.SERVICE_PROVIDER:
                return "Prestador de Serviço"
            case PartyRoleCode.PRODUCER:
                return "Produtor"
            case PartyRoleCode.PEER_COMPANY:
                return "Congenere"
            case PartyRoleCode.SUB_POLICYHOLDER:
                return "Sub Estipulante"
            case PartyRoleCode.REINSURER:
                return "Ressegurador"
            case PartyRoleCode.OTHERS:
                return "Outros"
            case PartyRoleCode.ATTORNEY_IN_FACT:
                return "Preposto"
            case PartyRoleCode.POLICY_TAKER:
                return "Tomador"
            case PartyRoleCode.INSPECTOR:
                return "Vistoriador"
            case PartyRoleCode.ATTENDING_PHYSICIAN:
                return "Médico Assistente"
            case PartyRoleCode.SHAREHOLDER:
                return "Acionista"
            case PartyRoleCode.SPOUSE:
                return "Cônjuge"
            case PartyRoleCode.CONTACT:
                return "Contato"
            case PartyRoleCode.EMPLOYEE:
                return "Funcionário"
            case PartyRoleCode.DRIVER:
                return "Condutor"
            case PartyRoleCode.THIRD_PARTY:
                return "Terceiro"
            case PartyRoleCode.GUARANTOR:
                return "Fiador"
            case PartyRoleCode.SUPPLIER:
                return "Fornecedor"
            case PartyRoleCode.LEGAL_REPRESENTATIVE:
                return "Representante Legal"
            case PartyRoleCode.INSURANCE_BROKER:
                return "Broker"
            case PartyRoleCode.CLAIMANT:
                return "Reclamante"
            case PartyRoleCode.FEDERAL_AGENCY:
                return "Órgão Público Federal"
            case PartyRoleCode.STATE_AGENCY:
                return "Órgão Público Estadual"
            case PartyRoleCode.PARTNER:
                return "Parceiro"
            case PartyRoleCode.PROPERTY_RESPONSIBLE:
                return "Responsável da Propriedade"
            case PartyRoleCode.SURVEYOR:
                return "Inspetor"
            case PartyRoleCode.EXPERT:
                return "Perito"
            case PartyRoleCode.INSURER:
                return "Seguradora"
            case PartyRoleCode.PARTICIPANT:
                return "Participante"
            case PartyRoleCode.ACCOUNT_MANAGER:
                return "Chefe de Conta"
            case PartyRoleCode.PAYEE:
                return "Favorecido"
            case PartyRoleCode.PARTNER_OWNER:
                return "Sócio / Proprietário"
            case PartyRoleCode.ADVISORY:
                return "Assessoria"
            case PartyRoleCode.INTERMEDIARY:
                return "Intermediário"
            case _:
                return "Código desconhecido"


class CommunicationMethod(BaseModel):
    type: CommunicationMethodTypes = Field(alias="codigo")
    description: str = Field(alias="descricao")
    area_code: Optional[int] = Field(alias="ddd", default=None)


class PartyAddress(BaseModel):
    postal_code: int = Field(alias="cep")
    neighborhood: str = Field(alias="bairro")
    city: str = Field(alias="cidade")
    number: str = Field(alias="numero")
    state_code: int = Field(alias="codigoUf")  # TODO: Get Codes
    street: str = Field(alias="endereco")
    complement: str = Field(alias="complemento")
    address_type: int = Field(alias="tipoEndereco", default=1)  # TODO: Check if this is always 1 Why?
    is_main_address: bool = Field(alias="enderecoPrincipal", default=True)


class LegalIdentity(BaseModel):
    name: str = Field(alias="nome")
    party_type: PartyType = Field(alias="tipoPessoa")
    report_social_name: bool = Field(alias="informarNomeSocial", default=False)
    social_name: Optional[str] = Field(alias="nomeSocial", default=None)
    document: str = Field(alias="cpfCnpj")
    details: PartyDetails = Field(alias="detalhes")
    roles: list[PartyRole] = Field(alias="papeis")
    communication_methods: Optional[list[CommunicationMethod]] = Field(alias="meiosComunicacao", default=None)
    addresses: Optional[list[PartyAddress]] = Field(alias="enderecos", default=None)


class TransmissionData(BaseModel):
    harvest: int = Field(alias="safra")
    quotation_id: str = Field(alias="numeroProposta", max_length=15)
    client_city_bacen_code: str = Field(alias="codigoBacenMunicipioCliente")
    product_code: int = Field(alias="codigoProduto")
    calculation_base_date: date = Field(alias="dataBaseCalculo")
    policy_type: int = Field(alias="tipoApolice", default=PolicyTypes.INDIVIDUAL)
    section_number: int = Field(alias="secao", exclude=True)
    ## Endorsement
    endorsement_type_code: Optional[EndorsementCode] = Field(
        alias="codigoTipoEndosso",
        default=None,
    )
    endorsement_note: Optional[str] = Field(
        alias="textoLivreEndosso",
        default=None,
    )
    related_endorsement_id: Optional[int] = Field(alias="idEndossoRelacionado", default=None)
    related_endorsement_note: Optional[str] = Field(
        alias="textoLivreEndossoRelacionado",
        default=None,
    )
    ipf_value: float = Field(alias="valorIpf", default=0.0)
    ##
    parties: list[LegalIdentity] = Field(alias="pessoas")
    locations: list[Location] = Field(alias="locais")
    insurance_term: InsuranceTerm = Field(alias="vigenciaSeguro")
    subsidy: Subsidy = Field(alias="subvencao")
    premium: Premium = Field(alias="premio")
    billing: Billing = Field(alias="cobranca")
    commission_rules: CommissionRules = Field(alias="rolComissionamento")

    @computed_field(alias="secao")
    @property
    def section(self) -> str:
        return f"Seção {self.section_number}"
