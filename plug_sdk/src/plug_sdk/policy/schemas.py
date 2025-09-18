from datetime import datetime
from plug_sdk.base_model import BaseModel, Field
from typing import Any, Optional
from .transmission_schemas import TransmissionData
from enum import StrEnum


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


class GetProposalResponse(BaseModel):
    status_id: int = Field(
        ..., alias="cd_status", description="ID of the proposal and/or policy status"
    )
    status_name: str = Field(
        ...,
        alias="nm_status",
        description="Description of the proposal and/or policy status",
    )
    proposal_number: int = Field(
        ...,
        alias="cd_proposta",
        description="Proposal number corresponding to the queried proposal",
    )
    endorsement_id: int = Field(
        ..., alias="id_endosso", description="Endorsement ID of the queried proposal"
    )
    policy_number: int = Field(
        ...,
        alias="cd_apolice",
        description="Policy number corresponding to the queried proposal",
    )
    policy_id: int = Field(
        ...,
        alias="id_apolice",
        description="Policy ID corresponding to the queried proposal",
    )
    issue_date: datetime = Field(
        ..., alias="dt_emissao", description="Issue date in the ERP"
    )


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
