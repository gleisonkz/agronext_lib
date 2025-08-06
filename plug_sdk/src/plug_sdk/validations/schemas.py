from typing import Optional

from plug_sdk.base_model import BaseModel, Field, model_validator


class AddressSearchRequest(BaseModel):
    state: Optional[str] = Field(default=None, alias="uf")
    street: Optional[str] = Field(default=None, alias="logradouro")
    city: Optional[str] = Field(default=None, alias="localidade")

    @model_validator(mode="after")
    def validate_fields(self) -> "AddressSearchRequest":
        if not (self.state or (self.street and self.city)):
            raise ValueError("Either 'state' must be provided, or both 'street' and 'city' must be present.")
        return self


class PostalCodeSearchRequest(BaseModel):
    postal_code: str


class BaseAddressResponse(BaseModel):
    postal_code: str = Field(alias="cep")
    state: str = Field(alias="uf")
    city_number: int = Field(alias="numeroLocalidade")
    city: str = Field(alias="localidade")
    street: str = Field(alias="logradouro")
    street_type: str = Field(alias="tipoLogradouro")
    street_name: str = Field(alias="nomeLogradouro")
    neighborhood: str = Field(alias="bairro")
    postal_code_type: int = Field(alias="tipoCEP")
    abbreviation: str = Field(alias="abreviatura")

    # side: str = Field(alias="lado")
    # number_start: int = Field(alias="numeroInicial")
    # number_end: int = Field(alias="numeroFinal")


class PostalCodeSearchResponse(BaseAddressResponse):
    pass


class PostalBoxRange(BaseModel):
    number_start: int = Field(alias="nuInicial")
    number_end: int = Field(alias="nuFinal")


class AddressItem(BaseAddressResponse):
    # street_number: int = Field(alias="numeroLogradouro")
    # unit_name: str = Field(alias="nome")
    # unit_abbreviation: str = Field(alias="siglaUnidade")
    postal_boxes: list[PostalBoxRange] = Field(default_factory=list, alias="caixasPostais")


class PaginationLink(BaseModel):
    rel: str
    href: str


class PageInfo(BaseModel):
    size: int = Field(alias="size")
    total_elements: int = Field(alias="totalElements")
    total_pages: int = Field(alias="totalPages")
    page_number: int = Field(alias="number")


class AddressSearchResponse(BaseModel):
    items: Optional[list[BaseAddressResponse]] = Field(alias="itens", default_factory=list)
    links: list[PaginationLink] = Field(alias="links", default_factory=list)
    page: PageInfo


class TechnicalRestrictionRequest(BaseModel):
    cpf_cnpj: str
    application: str


class TechnicalRestrictionResponse(BaseModel):
    cpf_cnpj: str = Field(alias="cpfCnpj")
    name: str | None = Field(None, alias="nome")
    message: str = Field(alias="mensagem")
    restriction: bool = Field(alias="restricao")
