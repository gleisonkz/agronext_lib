from datetime import datetime
from enum import IntEnum, StrEnum
from typing import Any, Optional

from plug_sdk.base_model import BaseModel, Field, RootModel

from .transmission_schemas import TransmissionData


class ReportType(IntEnum):
    CROPS = 612
    PASTURES = 1000253


class ResponseCodes(StrEnum):
    SUCCESS = "0"
    ERROR = "100036"


class SubmitQuotationRequest(BaseModel):
    data: TransmissionData


class BaseERPResponse(BaseModel):
    code: str = Field(alias="codigoRetorno")
    message: str = Field(alias="mensagem")


class SubmitQuotationResponse(BaseERPResponse):
    error_description: Optional[Any] = Field(alias="descricaoErro", default=None)
    proposal_id: Optional[str] = Field(alias="idEndosso", default=None)


class GetProposalRequest(BaseModel):
    quotation_id: int = Field(alias="numeroProposta")


class ProposalStatus(BaseModel):
    status_id: int = Field(..., alias="cd_status", description="ID of the proposal and/or policy status")
    status_name: Optional[str] = Field(alias="nm_status", description="Description of the proposal and/or policy status", default=None)
    quotation_id: int = Field(alias="cd_proposta", description="Proposal number corresponding to the queried proposal")
    endorsement_id: int = Field(alias="id_endosso", description="Endorsement ID of the queried proposal")
    policy_code: Optional[int] = Field(alias="cd_apolice", description="Policy number corresponding to the queried proposal", default=None)
    policy_id: int = Field(alias="id_apolice", description="Policy ID corresponding to the queried proposal")
    issue_date: datetime = Field(alias="dt_emissao", description="Issue date in the ERP")


GetProposalResponse = RootModel[list[ProposalStatus]]


class RejectProposalRequest(BaseModel):
    proposal_id: int = Field(alias="idEndosso")
    description: str = Field(alias="textoLivre")
    motive_code: int = Field(alias="codigoMotivoRecusa", default=1)


class RejectProposalResponse(BaseERPResponse):
    pass


class IssuePolicyRequest(BaseModel):
    proposal_id: int = Field(alias="idEndosso")


class IssuePolicyResponse(BaseERPResponse):
    policy_id: Optional[str] = Field(alias="numeroApolice", default=None)


class PolicyDocumentResponse(BaseModel):
    report_base64_pdf: str = Field(..., alias="base64")
