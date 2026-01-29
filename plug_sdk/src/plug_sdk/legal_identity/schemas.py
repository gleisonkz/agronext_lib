from datetime import datetime
from typing import Optional
from enum import StrEnum

from plug_sdk.base_model import BaseModel, Field


class NaturalPersonRequest(BaseModel):
    cpf: str = Field(alias="cpf", description="CPF of the natural person")


class LegalEntityRequest(BaseModel):
    cnpj: str = Field(alias="cnpj", description="CNPJ of the legal entity")


class Metadata(BaseModel):
    last_event_id: str = Field(
        alias="lastEventID",
        description="UUID of the last event in Neoway for the legalentity",
    )
    last_update: datetime = Field(
        alias="lastUpdate",
        description="Date of the last update in Neoway for the legalentity",
    )
    processing_timestamp: datetime = Field(
        alias="processingTimeStamp",
        description="Processing date in Neoway for the legalentity",
    )
    schema_id: int = Field(
        alias="schemaID", description="Schema ID of the legalentity information"
    )
    source: list[str] = Field(
        alias="source", description="Sources of legalentity information"
    )


class CnpjRegularityStatus(StrEnum):
    ACTIVE = "ATIVA"
    INACTIVE = "INAPTA"
    SUSPENDED = "SUSPENSA"
    CLOSED = "BAIXADA"
    NULL = "NULA"


class RegistrationStatus(BaseModel):
    date: datetime = Field(alias="data", description="Date of registration situation")
    status: CnpjRegularityStatus | str = Field(
        alias="status", description="LegalEntity status"
    )


class LegalEntityMetadata(Metadata):
    public_debt: Optional[Metadata] = Field(
        None, alias="empresaPgfnDau", description="Debts in PGFN and DAU"
    )
    tax_health: Optional[Metadata] = Field(
        None, alias="empresaSaudeTributaria", description="Tax and fiscal health"
    )
    sintegra: Optional[Metadata] = Field(
        None, alias="empresaSintegra", description="Sintegra fiscal data"
    )


class NegativeCertificate(BaseModel):
    name: str = Field(alias="nome")


class TaxHealthInfo(BaseModel):
    negative_certificates: list[NegativeCertificate] = Field(
        alias="cnds", default_factory=list
    )


class UnionDebt(BaseModel):
    registration_number: Optional[str] = Field(alias="inscricao")
    nature: Optional[str] = Field(alias="natureza")
    value: Optional[float] = Field(alias="valorInscricaoDevido")


class UnionDebtInfo(BaseModel):
    total_debts: Optional[float] = Field(alias="totalDividas")
    debts: list[UnionDebt] = Field(
        alias="dividas",
        description="list of debts in PGFN and DAU",
        default_factory=list,
    )


class StateRegistration(BaseModel):
    state: str = Field(alias="ie")


class SintegraInfo(BaseModel):
    registrations: list[StateRegistration] = Field(
        alias="inscricoes", default_factory=list
    )


class LegalEntity(BaseModel):
    name: Optional[str] = Field(
        None, alias="razaoSocial", description="Corporate name of the legalentity"
    )
    registration_info: Optional[RegistrationStatus] = Field(
        None,
        alias="situacaoCadastral",
        description="Cadastral situation of the legalentity",
    )


class PlugLegalEntityResponse(BaseModel):
    cnpj: str = Field(alias="_id", description="CNPJ of the legalentity")
    legal_entity: LegalEntity = Field(
        alias="empresa", description="LegalEntity information object"
    )
    union_debt_info: Optional[UnionDebtInfo] = Field(
        alias="empresaPgfnDau", default=None
    )
    tax_health_info: Optional[TaxHealthInfo] = Field(
        alias="empresaSaudeTributaria", default=None
    )
    sintegra_info: Optional[SintegraInfo] = Field(alias="empresaSintegra", default=None)


class LegalEntityResponse(BaseModel):
    cnpj: str = Field(alias="_id", description="CNPJ of the legalentity")
    trade_name: Optional[str] = Field(
        None, alias="razaoSocial", description="Corporate name of the legalentity"
    )
    registration_date: datetime = Field(
        alias="data", description="Date of registration situation"
    )
    status: str = Field(alias="status", description="LegalEntity status")


class CpfRegularityStatus(StrEnum):
    REGULAR = "REGULAR"
    PENDING_REGULARIZATION = "PENDENTE_DE_REGULARIZACAO"
    SUSPENDED = "SUSPENSO"
    CANCELED = "CANCELADO"
    DECEASED = "TITULAR_FALECIDO"
    NULL = "NULO"


class NaturalPersonInfo(BaseModel):
    name: str = Field(alias="nome", description="Full name of the naturalperson")
    status: CpfRegularityStatus | str = Field(
        alias="situacao", description="Status of the naturalperson"
    )


class NaturalPersonInfoMetadata(Metadata):
    """Metadata for naturalperson information."""

    person: Metadata = Field(
        alias="pessoa",
        description="Metadata information for the naturalperson",
    )
    neoway_entity: Metadata = Field(
        alias="entity-neoway-pessoa",
        description="Neoway entity information about the naturalperson",
    )


class PlugNaturalPersonResponse(BaseModel):
    cpf: str = Field(alias="_id", description="CPF of the naturalperson")
    birth_date: Optional[datetime] = Field(
        None, alias="dataNascimento", description="Birth date of the naturalperson"
    )
    person_info: NaturalPersonInfo = Field(
        alias="pessoa", description="Detailed naturalperson information"
    )
    # metadata: dict[str, Metadata] = Field(alias="_metadata", description="Main metadata information")


class NaturalPersonResponse(BaseModel):
    cpf: str = Field(alias="_id", description="CPF of the naturalperson")
    birth_date: Optional[datetime] = Field(
        None, alias="dataNascimento", description="Birth date of the naturalperson"
    )
    name: str = Field(alias="nome", description="Full name of the naturalperson")
    status: CpfRegularityStatus = Field(
        alias="situacao", description="Status of the naturalperson"
    )
