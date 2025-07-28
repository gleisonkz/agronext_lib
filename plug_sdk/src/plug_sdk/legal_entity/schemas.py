from plug_sdk.base_model import BaseModel, Field
from typing import Optional


class PersonMetadata(BaseModel):
    last_event_id: str = Field(..., alias="lastEventID")
    last_update: str = Field(..., alias="lastUpdate")
    processing_timestamp: str = Field(..., alias="processingTimestamp")
    schema_id: str = Field(..., alias="schemaID")
    source: list[str]


class PersonDetails(BaseModel):
    name: str = Field(..., alias="nome")
    status: str = Field(..., alias="situacao")


class IndividualResponse(BaseModel):
    id: str = Field(..., alias="_id")
    metadata: dict[str, PersonMetadata] = Field(..., alias="_metadata")
    birth_date: str = Field(..., alias="dataNascimento")
    person: PersonDetails = Field(..., alias="pessoa")


class IndividualRequest(BaseModel):
    cpf: str


class CompanyRequest(BaseModel):
    cnpj: str


class CompanyResponse(BaseModel):
    error: Optional[str] = Field(None, alias="erro")
    message: Optional[str] = Field(None, alias="mensagem")
