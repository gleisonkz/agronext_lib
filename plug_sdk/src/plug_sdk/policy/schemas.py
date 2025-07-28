from plug_sdk.base_model import BaseModel, Field
from typing import Any, Optional
from .transmission_schemas import TransmissionData
from enum import StrEnum


class TransmissionRequest(BaseModel):
    data: TransmissionData


class RejectProposalRequest(BaseModel):
    proposal_id: int = Field(alias="idEndosso")
    free_text: str = Field(alias="textoLivre")


class IssuePolicyRequest(BaseModel):
    proposal_id: int = Field(alias="idEndosso")


class ResponseCodes(StrEnum):
    SUCCESS = "0"
    ERROR = "100036"


class TransmissionResponse(BaseModel):
    code: str = Field(alias="codigoRetorno")
    message: str = Field(alias="mensagem")
    error_description: Optional[Any] = Field(alias="descricaoErro", default=None)
    proposal_id: Optional[str] = Field(alias="idEndosso", default=None)


class InstallmentItem(BaseModel):
    policy_code: Optional[int] = Field(None, alias="cd_apolice")
    proposal_code: int = Field(..., alias="cd_proposta")
    endorsement_id: int = Field(..., alias="id_endosso")
    endorsement_number: int = Field(..., alias="nr_endosso")
    installment_number: int = Field(..., alias="nr_parcela")
    title: str = Field(..., alias="titulo")
    status: str = Field(..., alias="situacao")
    payment_date: str = Field(..., alias="dt_pagamento")
    clearing_date: str = Field(..., alias="dt_baixa")
    amount_received: str = Field(..., alias="valor_recebido")
    premium_amount: str = Field(..., alias="vl_tarifario")
    iof_value: str = Field(..., alias="vl_iof")
    total_amount: str = Field(..., alias="vl_total")
    representation_date: str = Field(..., alias="dt_representacao")
    due_date: str = Field(..., alias="dt_vencimento")


class InstallmentResponse(BaseModel):
    installments: list[InstallmentItem] = Field(..., alias="consulta_parcela")


class InstallmentRequest(BaseModel):
    policy_id: str = Field(..., alias="idEndosso")
    installment_number: str = Field(..., alias="numeroParcela")


class BoletoRequest(BaseModel):
    policy_id: str = Field(..., alias="idEndosso")
    installment_number: str = Field(..., alias="numeroParcela")


class BoletoResponse(BaseModel):
    policy_id: str = Field(..., alias="idEndosso")
    installment_number: str = Field(..., alias="parcela")
    boleto_base64_pdf: str = Field(..., alias="boleto")


class SubsidyLimitItem(BaseModel):
    modality_description: str = Field(..., alias="dsModalidade")
    committed_balance: float = Field(..., alias="vlSaldoComprometido")
    available_balance: float = Field(..., alias="vlSaldoDisponivel")


class SubsidyLimits(BaseModel):
    insured_limits: list[SubsidyLimitItem] = Field(..., alias="limiteSegurado")


class SubsidyLimitResponse(BaseModel):
    insured_document: str = Field(..., alias="nrCpfCnpjSegurado")
    insured_name: str = Field(..., alias="nmSegurado")
    fiscal_year: str = Field(..., alias="anPeriodoExercicio")
    insured_financial_limits: SubsidyLimits = Field(..., alias="limitesSegurado")


class SubsidyLimitRequest(BaseModel):
    cpf_cnpj: str
    year: str
