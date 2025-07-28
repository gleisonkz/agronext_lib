from plug_sdk.base_model import BaseModel, Field


class AddressLookupRequest(BaseModel):
    postal_code: str


class AddressLookupResponse(BaseModel):
    cep: str
    state: str = Field(..., alias="uf")
    locality_number: int = Field(..., alias="numeroLocalidade")
    city: str = Field(..., alias="localidade")
    street: str = Field(..., alias="logradouro")
    street_type: str = Field(..., alias="tipoLogradouro")
    street_name: str = Field(..., alias="nomeLogradouro")
    abbreviation: str = Field(..., alias="abreviatura")
    neighborhood: str = Field(..., alias="bairro")
    cep_type: int = Field(..., alias="tipoCEP")
    side: str = Field(..., alias="lado")
    number_start: int = Field(..., alias="numeroInicial")
    number_end: int = Field(..., alias="numeroFinal")


class TechnicalRestrictionRequest(BaseModel):
    cpf_cnpj: str
    application: str


class TechnicalRestrictionResponse(BaseModel):
    cpf_cnpj: str = Field(..., alias="cpfCnpj")
    name: str | None = Field(None, alias="nome")
    message: str = Field(..., alias="mensagem")
    restriction: bool = Field(..., alias="restricao")
