from dataclasses import dataclass, field
from typing import TypedDict


class CellConfig(TypedDict, total=False):
    label: str
    value: str
    width: str


@dataclass
class ApplicantData:
    name: str = ""
    cpf: str = ""
    birth_date: str = ""
    social_name: str = ""
    document_number: str = ""
    issuing_authority: str = ""
    issue_date: str = ""
    marital_status: str = ""
    main_email: str = ""
    phone_number: str = ""
    phone_type: str = ""
    is_whatsapp: str = ""
    professional_category: str = ""
    income: str = ""


@dataclass
class AddressData:
    zip_code: str = ""
    country: str = ""
    state: str = ""
    city: str = ""
    neighborhood: str = ""
    street: str = ""
    number: str = ""
    complement: str = ""


@dataclass
class PoliticalExposureData:
    is_pep: str = ""
    pep_name: str = ""


@dataclass
class CoverageData:
    name: str = ""
    policy_limit_brl: str = ""
    deductible_pct: str = ""
    coverage_rate_pct: str = ""
    tariff_premium: str = ""
    insured_area_ha: str = ""
    plot_count: str = ""
    net_premium: str = ""
    federal_subsidy_brl: str = ""
    state_subsidy_brl: str = ""
    applicant_value: str = ""


@dataclass
class PaymentData:
    payment_method: str = ""
    number_of_installments: str = ""
    net_premium: str = ""
    policy_cost: str = ""
    iof: str = ""
    total_premium: str = ""
    installments: list[list[str]] = field(default_factory=list)


@dataclass
class BrokerData:
    name: str = ""
    susep: str = ""
    commission_pct: str = ""
    phone: str = ""
    emails: list[str] = field(default_factory=list)
    phones: list[str] = field(default_factory=list)


@dataclass
class PropertyData:
    name: str = ""
    ownership_type: str = ""
    coordinates: str = ""
    zip_code: str = ""
    country: str = ""
    state: str = ""
    city: str = ""
    bacen_code: str = ""
    neighborhood: str = ""
    street: str = ""
    number: str = ""


@dataclass
class RiskQuestionItem:
    """Represents a single question in the risk questionnaire."""

    question: str = ""
    answer: str = ""
    extra_fields: list[tuple[str, str]] = field(default_factory=list)  # [(label, value), ...]


@dataclass
class RiskQuestionnaireData:
    questions: list[RiskQuestionItem] = field(default_factory=list)


@dataclass
class SubsidyQuestionItem:
    """Represents a single question in the subsidy section."""

    question: str = ""
    answer: str = ""
    extra_fields: list[tuple[str, str]] = field(default_factory=list)  # [(label, value), ...]


@dataclass
class SubsidyData:
    questions: list[SubsidyQuestionItem] = field(default_factory=list)


@dataclass
class BeneficiaryData:
    name: str = ""
    cpf: str = ""
    birth_date: str = ""
    social_name: str = ""
    email: str = ""
    phone: str = ""
    percentage: str = ""
    value: str = ""
    relationship: str = ""


@dataclass
class AuthorizedPersonData:
    name: str = ""
    social_name: str = ""
    relationship: str = ""
    phone: str = ""


@dataclass
class AuthorizationTermData:
    applicant_name: str = ""
    proposal_number: str = ""
    has_account: str = ""
    authorization_text: str = ""
    bank_name: str = ""
    agency_number: str = ""
    agency_digit: str = ""
    account_number: str = ""
    account_digit: str = ""
    account_type: str = ""
    joint_account: str = ""
    discharge_text: str = ""
    liability_text: str = ""
    ratification_text: str = ""


@dataclass
class AuthorizationBeneficiaryData:
    beneficiary_name: str = ""
    proposal_number: str = ""
    authorization_question: str = ""
    authorization_answer: str = ""
    authorization_text: str = ""
    beneficiary_full_name: str = ""
    beneficiary_cpf: str = ""
    beneficiary_relationship: str = ""
    bank_name: str = ""
    agency_number: str = ""
    agency_digit: str = ""
    account_number: str = ""
    account_digit: str = ""
    account_type: str = ""
    joint_account: str = ""
    pix_type: str = ""
    pix_key: str = ""
    observation_text: str = ""
    discharge_text: str = ""
    liability_text: str = ""
    ratification_text: str = ""


@dataclass
class LgpdConsentData:
    title: str = ""
    consent_text: str = ""
    signature_name: str = ""
    signature_cpf: str = ""


@dataclass
class ProponentDeclarationData:
    content_html: str = ""
    content_bold: bool = False
    checkbox_text: str = ""
    checkbox_checked: bool = False
    checkbox_align: str = "top"  # "top" ou "center"
    checkbox_bold: bool = False
    left_label: str = ""
    center_label: str = ""
    right_label: str = ""
    observation_text: str = ""
    footer_bordered_text: str = ""


@dataclass
class ModalityOption:
    label: str = ""
    checked: bool = False


@dataclass
class FederalSubsidyTermData:
    ministry_header: str = ""
    committee_text: str = ""
    secretariat_text: str = ""
    main_title: str = ""
    section_title: str = ""
    intro_text: str = ""
    modality_options: list[ModalityOption] = field(default_factory=list)
    declaration_intro: str = ""
    declarations: list[str] = field(default_factory=list)
    signature_date_text: str = ""
    signature_text: str = ""
    # Seção II
    section2_title: str = ""
    section2_question: str = ""
    section2_options: list[str] = field(default_factory=list)
    section2_date_text: str = ""
    section2_responsible_text: str = ""
    section2_cpf_text: str = ""
    section2_signature_text: str = ""


@dataclass
class StateSubsidyTermData:
    government_header: str = ""
    annex_title: str = ""
    intro_text: str = ""
    declarations: list[str] = field(default_factory=list)
    date_location_text: str = ""
    signature_text: str = ""
    name_cpf_text: str = ""


@dataclass
class StateAuthorizationTermData:
    logo_path: str = ""
    government_header: str = ""
    government_subheader: str = ""
    annex_title: str = ""
    intro_text: str = ""
    declarations: list[str] = field(default_factory=list)
    date_location_text: str = ""
    signature_text: str = ""
    name_cpf_text: str = ""


@dataclass
class HeaderData:
    logo_path: str = ""
    main_coverage: str = ""
    validity_period: str = ""
    reception_date: str = ""
    page: str = "1 de 13"
    crop: str = ""
    bacen_code: str = ""
    harvest: str = ""
    insurer: str = ""
    insurer_cnpj: str = ""
    susep: str = ""
    mapa_code: str = ""
    proposal_number: str = ""
    policy: str = ""


@dataclass
class PDFData:
    header: HeaderData = field(default_factory=HeaderData)
    applicant: ApplicantData = field(default_factory=ApplicantData)
    residential_address: AddressData = field(default_factory=AddressData)
    political_exposure: PoliticalExposureData = field(default_factory=PoliticalExposureData)
    coverage: CoverageData = field(default_factory=CoverageData)
    payment: PaymentData = field(default_factory=PaymentData)
    broker: BrokerData = field(default_factory=BrokerData)
    property: PropertyData = field(default_factory=PropertyData)
    risk_questionnaire: RiskQuestionnaireData = field(default_factory=RiskQuestionnaireData)
    subsidy: SubsidyData = field(default_factory=SubsidyData)
    beneficiaries: list[BeneficiaryData] = field(default_factory=list)
    has_authorized_persons: str = ""
    authorized_persons: list[AuthorizedPersonData] = field(default_factory=list)
    risk_data: list[list[str]] = field(default_factory=list)
    plot_coordinates: list[list[str]] = field(default_factory=list)
    croqui_bytes: bytes = b""
    additional_data: str = ""
    observations: str = ""
    grace_period_html: str = ""
    coverage_restrictions_html: str = ""
    available_documents_html: str = ""
    excluded_risks_html: str = ""
    authorization_term: AuthorizationTermData = field(default_factory=AuthorizationTermData)
    authorization_beneficiary: AuthorizationBeneficiaryData = field(default_factory=AuthorizationBeneficiaryData)
    lgpd_consent: LgpdConsentData = field(default_factory=LgpdConsentData)
    proponent_declaration: ProponentDeclarationData = field(default_factory=ProponentDeclarationData)
    federal_subsidy_term: FederalSubsidyTermData = field(default_factory=FederalSubsidyTermData)
    state_subsidy_term: StateSubsidyTermData = field(default_factory=StateSubsidyTermData)
    state_authorization_term: StateAuthorizationTermData = field(default_factory=StateAuthorizationTermData)
    information_html_blocks: list[str] = field(default_factory=list)
    total_pages: int = 13
