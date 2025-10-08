from typing import Optional

from plug_sdk.base_model import BaseModel, Field


class PostalCodeLookupRequest(BaseModel):
    postal_code: str


class AddressLookupRequest(BaseModel):
    state: Optional[str] = Field(alias="uf", default=None)
    city: Optional[str] = Field(alias="localidade", default=None)
    street: Optional[str] = Field(alias="logradouro", default=None)


class PostalCodeLookupResponse(BaseModel):
    cep: str = Field(alias="cep")
    state: str = Field(alias="uf")
    locality_number: int = Field(alias="numeroLocalidade")
    city: str = Field(alias="localidade")
    street: str = Field(alias="logradouro")
    street_name: str = Field(alias="nomeLogradouro")
    neighborhood: str = Field(alias="bairro")
    abbreviation: Optional[str] = Field(alias="abreviatura", default=None)
    street_type: Optional[str] = Field(alias="tipoLogradouro", default=None)
    cep_type: Optional[int] = Field(alias="tipoCEP", default=None)
    complement: Optional[str] = Field(alias="complemento", default=None)
    side: Optional[str] = Field(alias="lado", default=None)
    number_start: Optional[int] = Field(alias="numeroInicial", default=None)
    number_end: Optional[int] = Field(alias="numeroFinal", default=None)


class AddressLookupPage(BaseModel):
    size: int = Field(..., alias="size")
    total_elements: int = Field(..., alias="totalElements")
    total_pages: int = Field(..., alias="totalPages")
    number: int = Field(..., alias="number")


class AddressLookupLink(BaseModel):
    href: Optional[str] = Field(alias="href", default=None)
    rel: Optional[str] = Field(alias="rel", default=None)


class AddressLookupResponse(BaseModel):
    addresses: list[PostalCodeLookupResponse] = Field(alias="itens", default_factory=list)
    links: list[AddressLookupLink] = Field(alias="links", default_factory=list)
    pagination: AddressLookupPage = Field(alias="page", default=None)


class TechnicalRestrictionRequest(BaseModel):
    cpf_cnpj: str = Field(alias="cpfCnpj")


class TechnicalRestrictionResponse(BaseModel):
    cpf_cnpj: str = Field(alias="cpfCnpj")
    name: str | None = Field(alias="nome", default=None)
    message: str = Field(alias="mensagem")
    restriction: bool = Field(alias="restricao")
