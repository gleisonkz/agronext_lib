from enum import IntEnum, StrEnum
from typing import Optional

from plug_sdk.base_model import BaseModel, EmailStr, Field


class ProductCodes(IntEnum):
    RCO = 326
    RISCO_ENGENHARIA = 346
    AERONÁUTICO_RETA = 301
    GARANTIA_SETOR_PRIVADO = 349
    GARANTIA_SETOR_PUBLICO = 348
    CAMINHÕES_APISUL = 352
    CARGO_MARINE_TRANSP_NACIONAL = 366
    CARGO_MARINE_RCTR_C = 367
    CARGO_MARINE_RCF_DC = 368
    CARGO_MARINE_RCTR_VI = 369


class NotificationTypes(IntEnum):
    EMAIL = 1


class EmailTemplateTypes(IntEnum):
    INTERNAL = 1
    EXTERNAL = 2
    SIMPLE = 3


class MimeTypes(StrEnum):
    PDF = "application/pdf"
    PNG = "image/png"
    JPEG = "image/jpeg"
    JPG = "image/jpg"
    TXT = "text/plain"
    DOC = "application/msword"
    DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    XLS = "application/vnd.ms-excel"
    XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    PPT = "application/vnd.ms-powerpoint"
    PPTX = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    ZIP = "application/zip"
    RAR = "application/x-rar-compressed"
    GIF = "image/gif"
    BMP = "image/bmp"
    CSV = "text/csv"
    HTML = "text/html"
    XML = "application/xml"
    JSON = "application/json"


class Recipient(BaseModel):
    name: str = Field(alias="nome")
    email: EmailStr = Field(alias="email")


class Content(BaseModel):
    header: str = Field(alias="descricao")
    body: str = Field(alias="conteudo")


class AttachmentOptions(BaseModel):
    mime_type: MimeTypes = Field(alias="mime")


class Attachments(BaseModel):
    name: str = Field(alias="nome")
    options: AttachmentOptions = Field(alias="opcoes")
    base_64: str = Field(alias="base64")


class Applications(StrEnum):
    AGRONEXT = "AgroNext"
    PLUG = "Plug"


class EmailNotificationRequest(BaseModel):
    application: Applications = Field(alias="aplicacao")
    notification_type: NotificationTypes = Field(alias="tipoNotificacao", default=NotificationTypes.EMAIL)
    template_type: EmailTemplateTypes = Field(alias="codigoEmail", default=EmailTemplateTypes.SIMPLE)

    to: list[Recipient] = Field(alias="para", default_factory=list)
    cc: Optional[list[Recipient]] = Field(alias="copia", default=None)
    bcc: Optional[list[Recipient]] = Field(alias="copiaOculta", default=None)

    subject: str = Field(alias="assunto")
    description: str = Field(alias="descricaoEmail")

    quotation_number: Optional[str] = Field(alias="numeroCotacao", default=None)
    proposal_number: Optional[str] = Field(alias="numeroProposta", default=None)
    policy_number: Optional[str] = Field(alias="numeroApolice", default=None)
    proposal_id: Optional[int] = Field(alias="idEndosso", default=None)
    product_code: Optional[ProductCodes] = Field(alias="codigoProduto", default=None)

    body: list[Content] = Field(alias="dados", default_factory=list)
    attachments: Optional[list[Attachments]] = Field(alias="anexos", default=None)


class EmailNotificationResponse(BaseModel):
    message: str = Field(alias="mensagem")
