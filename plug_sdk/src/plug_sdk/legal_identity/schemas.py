from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class BrokerRequest(BaseModel):
    cpf_cnpj: str = Field(..., alias="cpfCnpj", description="CPF or CNPJ of the broker")


class NaturalPersonRequest(BaseModel):
    cpf: str = Field(..., alias="cpf", description="CPF of the natural person")


class LegalEntityRequest(BaseModel):
    cnpj: str = Field(..., alias="cnpj", description="CNPJ of the legal entity")


class Metadata(BaseModel):
    last_event_id: str = Field(
        ...,
        alias="lastEventID",
        description="UUID of the last event in Neoway for the legalentity",
    )
    last_update: datetime = Field(
        ...,
        alias="lastUpdate",
        description="Date of the last update in Neoway for the legalentity",
    )
    processing_timestamp: datetime = Field(
        ...,
        alias="processingTimeStamp",
        description="Processing date in Neoway for the legalentity",
    )
    schema_id: int = Field(
        ..., alias="schemaID", description="Schema ID of the legalentity information"
    )
    source: List[str] = Field(
        ..., alias="source", description="Sources of legalentity information"
    )


class PublicDebtInfo(Metadata):
    """Information about PGFN and DAU debts."""


class TaxHealthInfo(Metadata):
    """Information about legalentity tax and fiscal health."""


class SintegraInfo(Metadata):
    """Information about legalentity fiscal situation from Sintegra."""


class RegistrationStatus(BaseModel):
    date: datetime = Field(
        ..., alias="data", description="Date of registration situation"
    )
    status: str = Field(..., alias="status", description="LegalEntity status")


class LegalEntity(BaseModel):
    name: Optional[str] = Field(
        None, alias="razaoSocial", description="Corporate name of the legalentity"
    )
    cadastral_situation: Optional[RegistrationStatus] = Field(
        None,
        alias="situacaoCadastral",
        description="Cadastral situation of the legalentity",
    )


class LegalEntityResponse(BaseModel):
    legalentity_id: str = Field(..., alias="_id", description="CNPJ of the legalentity")
    metadata: Metadata = Field(
        ..., alias="_metadata", description="Main metadata information"
    )
    legalentity: LegalEntity = Field(
        ..., alias="empresa", description="LegalEntity information object"
    )
    public_debt: Optional[PublicDebtInfo] = Field(
        None, alias="empresaPgfnDau", description="Debts in PGFN and DAU"
    )
    tax_health: Optional[TaxHealthInfo] = Field(
        None, alias="empresaSaudeTributaria", description="Tax and fiscal health"
    )
    sintegra: Optional[SintegraInfo] = Field(
        None, alias="empresaSintegra", description="Sintegra fiscal data"
    )


class NaturalPersonInfo(BaseModel):
    name: str = Field(..., alias="nome", description="Full name of the naturalperson")
    status: str = Field(
        ..., alias="situacao", description="Status of the naturalperson"
    )
    birth_date: Optional[datetime] = Field(
        None, alias="dataNascimento", description="Birth date of the naturalperson"
    )


class NaturalPersonResponse(BaseModel):
    naturalperson_id: str = Field(
        ..., alias="_id", description="CPF of the naturalperson"
    )
    metadata: Metadata = Field(
        ..., alias="_metadata", description="Main metadata information"
    )
    entity_neoway: Metadata = Field(
        ...,
        alias="entity-neoway-pessoa",
        description="Neoway entity information about the naturalperson",
    )
    naturalperson: NaturalPersonInfo = Field(
        ..., alias="pessoa", description="Detailed naturalperson information"
    )


class BrokerResponse(BaseModel):
    pass
