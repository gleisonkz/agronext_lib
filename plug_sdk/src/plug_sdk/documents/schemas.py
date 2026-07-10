from plug_sdk.base_model import BaseModel, Field


class FormDocumentRequest(BaseModel):
    document_type_code: int = Field(alias="codigoTipoDocumento", default=5)  # 5 = Endosso and is the only option available
    domain_code: int = Field(alias="codigoDominio", default=2)  # 2 = Endosso and is the only option available
    treatment_code: int = Field(alias="codigoTratamento", default=1)  # 1 = normal and is the only option available
    endorsement_id: int = Field(alias="idEndosso") # erp_id
    file_name: str = Field(alias="nomeArquivo")
    observation_code: int = Field(alias="codigoObservacao")
    reference_number: str = Field(alias="numeroReferencia")
    base64_content: str = Field(alias="base64")


class FormDocumentResponse(BaseModel):
    endorsement_id: int = Field(alias="idEndosso")
    document_id: int = Field(alias="idDocumento")
