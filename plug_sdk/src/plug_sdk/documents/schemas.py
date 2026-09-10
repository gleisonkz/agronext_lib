from enum import IntEnum, StrEnum

from plug_sdk.base_model import BaseModel, Field, RootModel

DOCUMENT_TYPE_CODE = 5  # 5 = Endosso and is the only option available
DOMAIN_CODE = 2  # 2 = Endosso and is the only option available
TREATMENT_CODE = 1  # 1 = normal and is the only option available


class ObservationCode(IntEnum):
    QUOTATION = 4
    PROPOSAL = 3
    POLICY = 1


class ObservationName(StrEnum):
    QUOTATION = "Cotacao"
    PROPOSAL = "Proposta"
    POLICY = "Apolice"
    DECLARATION = "Declaracao"


class FormDocumentRequest(BaseModel):
    document_type_code: int = Field(alias="codigoTipoDocumento", default=5)  # 5 = Endosso and is the only option available
    domain_code: int = Field(alias="codigoDominio", default=2)  # 2 = Endosso and is the only option available
    treatment_code: int = Field(alias="codigoTratamento", default=1)  # 1 = normal and is the only option available
    endorsement_id: int = Field(alias="idEndosso")  # erp_id
    file_name: str = Field(alias="nomeArquivo")
    observation_code: ObservationCode = Field(alias="codigoObservacao")
    reference_number: str = Field(alias="numeroReferencia")
    base64_content: str = Field(alias="base64")


class FormDocumentResponse(BaseModel):
    endorsement_id: int = Field(alias="idEndosso")
    document_id: int = Field(alias="idDocumento")


class FormDocumentItem(BaseModel):
    reference_number: str = Field(alias="nr_ref")
    file_name: str = Field(alias="img_documento_arquivo")
    document_id: int = Field(alias="id_documento")
    observation_name: ObservationName = Field(alias="nm_observacao")
    endorsement_id: int = Field(alias="id_endosso")


ListFormDocumentsResponse = RootModel[list[FormDocumentItem]]
