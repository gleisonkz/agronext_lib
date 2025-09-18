from pydantic import BaseModel, Field
from typing import List, Optional


class Recipient(BaseModel):
    name: str = Field(..., alias="nome", description="Recipient name")
    email: str = Field(..., alias="email", description="Recipient email")


class BodyField(BaseModel):
    description: str = Field(
        ..., alias="descricao", description="Field description in email body"
    )
    content: str = Field(
        ..., alias="conteudo", description="Field content in email body"
    )


class Attachment(BaseModel):
    mime: Optional[str] = Field(None, alias="mime", description="File MIME type")
    name: str = Field(..., alias="nome", description="Attachment file name")
    base64: str = Field(
        ..., alias="base64", description="File content in base64 encoding"
    )


class EmailNotificationRequest(BaseModel):
    quotation_number: Optional[str] = Field(
        None, alias="numeroCotacao", description="Quotation number"
    )
    proposal_number: Optional[str] = Field(
        None, alias="numeroProposta", description="Proposal number"
    )
    policy_number: Optional[str] = Field(
        None, alias="numeroApolice", description="Policy number"
    )
    endorsement_id: Optional[str] = Field(
        None, alias="idEndosso", description="Endorsement ID"
    )
    product_code: Optional[int] = Field(
        None, alias="codigoProduto", description="Product code"
    )
    application: str = Field(
        ..., alias="aplicacao", description="System performing the request"
    )
    notification_type: int = Field(
        ..., alias="tipoNotificacao", description="Notification type code"
    )
    email_description: str = Field(
        ..., alias="descricaoEmail", description="Brief description of the email"
    )
    email_code: int = Field(..., alias="codigoEmail", description="Email code")
    subject: Optional[str] = Field(None, alias="assunto", description="Email subject")

    to: List[Recipient] = Field(..., alias="para", description="Recipients")
    cc: Optional[List[Recipient]] = Field(
        None, alias="copia", description="Carbon copy recipients"
    )
    bcc: Optional[List[Recipient]] = Field(
        None, alias="copiaOculta", description="Blind carbon copy recipients"
    )

    body_fields: List[BodyField] = Field(
        ..., alias="dados", description="Email body fields"
    )

    attachments: Optional[List[Attachment]] = Field(
        None, alias="anexos", description="Email attachments"
    )
    attachment_options: Optional[List[str]] = Field(
        None, alias="opcoes", description="Attachment options"
    )


class EmailNotificationResponse(BaseModel):
    pass
