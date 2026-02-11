from typing import Optional, Self

from plug_sdk.base_model import BaseModel, Field
from enum import StrEnum


class InstallmentItem(BaseModel):
    policy_code: Optional[int] = Field(None, alias="cd_apolice")
    proposal_code: int = Field(alias="cd_proposta")
    endorsement_id: int = Field(alias="id_endosso")
    endorsement_number: int = Field(alias="nr_endosso")
    installment_number: int = Field(alias="nr_parcela")
    title: str = Field(alias="titulo")
    status: str = Field(alias="situacao")
    payment_date: Optional[str] = Field(None, alias="dt_pagamento")
    clearing_date: Optional[str] = Field(None, alias="dt_baixa")
    amount_received: str = Field(alias="valor_recebido")
    premium_amount: str = Field(alias="vl_tarifario")
    iof_value: str = Field(alias="vl_iof")
    total_amount: str = Field(alias="vl_total")
    representation_date: str = Field(alias="dt_representacao")
    due_date: str = Field(alias="dt_vencimento")


class InstallmentResponse(BaseModel):
    installments: list[InstallmentItem] = Field(alias="consulta_parcela")


class InstallmentRequest(BaseModel):
    proposal_id: int = Field(alias="idEndosso")
    installment: int = Field(alias="numeroParcela", default=0)


class BoletoRequest(BaseModel):
    proposal_id: int = Field(alias="idEndosso")
    installment: int = Field(alias="numeroParcela")


class BoletoResponse(BaseModel):
    policy_id: str = Field(alias="idEndosso")
    installment_number: int = Field(alias="parcela")
    boleto_base64_pdf: str = Field(alias="boleto")


class SubsidyLimitItem(BaseModel):
    modality_description: str = Field(alias="dsModalidade")
    committed_balance: float = Field(alias="vlSaldoComprometido")
    available_balance: float = Field(alias="vlSaldoDisponivel")


class SubsidyLimits(BaseModel):
    insured_limits: list[SubsidyLimitItem] = Field(alias="limiteSegurado")


class SubsidyLimitResponse(BaseModel):
    insured_document: str = Field(alias="nrCpfCnpjSegurado")
    insured_name: str = Field(alias="nmSegurado")
    fiscal_year: str = Field(alias="anPeriodoExercicio")
    insured_financial_limits: SubsidyLimits = Field(alias="limitesSegurado")


class SubsidyLimitRequest(BaseModel):
    cpf_cnpj: str = Field(alias="cpfCnpj")
    year: int = Field(alias="anoExercicio")


class CadinRequest(BaseModel):
    cpf_cnpj: str = Field(alias="cpfCnpj")


class CadinTransaction(BaseModel):
    id: int = Field(alias="id", description="Transaction ID")
    execution_datetime: str = Field(
        alias="dataHoraExecucao",
        description="Date and time of the request execution",
    )
    status: str = Field(alias="status", description="Request status")


class PartyCadinStatus(StrEnum):
    IN_GOOD_STANDING = "ADIMPLENTE"
    DELINQUENT = "INADIMPLENTE"
    NOT_LISTED = "NAO CONSTA"
    NOT_VERIFIED = "NAO_VALIDADO"


class CadinInsured(BaseModel):
    party_document: str = Field(
        alias="nrCpfCnpjSegurado", description="CPF or CNPJ of the insured"
    )
    party_status: PartyCadinStatus = Field(
        alias="stPessoa", description="Status of the consulted CPF or CNPJ"
    )


class CadinPlugResponse(BaseModel):
    transaction: CadinTransaction = Field(
        alias="transacao", description="Object with transaction information"
    )
    insured: CadinInsured = Field(
        alias="segurado", description="Object with consulted insured information"
    )


class CadinResponse(BaseModel):
    party_document: str
    party_status: PartyCadinStatus
    execution_date: str
    transaction_id: int
    transaction_status: str

    @classmethod
    def from_plug_response(cls, plug_response: CadinPlugResponse) -> Self:
        return cls(
            party_document=plug_response.insured.party_document,
            party_status=plug_response.insured.party_status,
            execution_date=plug_response.transaction.execution_datetime,
            transaction_id=plug_response.transaction.id,
            transaction_status=plug_response.transaction.status,
        )
