from typing import Optional

from .async_client import BaseAsyncClient, RequestOptions
from .external_users import (
    CreateExternalUserRequest,
    CreateExternalUserResponse,
    ExternalUserResponse,
    FilterExternalUsersRequest,
    FilterExternalUsersResponse,
    UpdateExternalUserRequest,
    UpdateExternalUserResponse,
)
from .financial import (
    BoletoRequest,
    BoletoResponse,
    CadinRequest,
    CadinResponse,
    InstallmentRequest,
    InstallmentResponse,
    SubsidyLimitRequest,
    SubsidyLimitResponse,
)
from .legal_identity import (
    BrokerRequest,
    BrokerResponse,
    LegalEntityRequest,
    LegalEntityResponse,
    NaturalPersonRequest,
    NaturalPersonResponse,
    PlugLegalEntityResponse,
    PlugNaturalPersonResponse,
)
from .notifications import (
    Applications,
    AttachmentOptions,
    Attachments,
    Content,
    EmailNotificationRequest,
    EmailNotificationResponse,
    EmailTemplateTypes,
    MimeTypes,
    NotificationTypes,
    ProductCodes,
    Recipient,
)
from .policy import (
    GetProposalRequest,
    GetProposalResponse,
    IssuePolicyRequest,
    IssuePolicyResponse,
    PolicyDocumentResponse,
    ProposalStatus,
    RejectProposalRequest,
    RejectProposalResponse,
    ReportType,
    SubmitQuotationRequest,
    SubmitQuotationResponse,
    TransmissionData,
)
from .validations import (
    AddressLookupRequest,
    AddressLookupResponse,
    PostalCodeLookupRequest,
    PostalCodeLookupResponse,
    TechnicalRestrictionRequest,
    TechnicalRestrictionResponse,
)


class PlugSDK:
    def __init__(
        self,
        base_url: str = "http://uatplug.essor.net",
        credentials: dict | None = None,
        headers: Optional[dict[str, str]] = None,
    ):
        self.client = BaseAsyncClient(base_url=base_url, headers=headers)

        self._eas_headers = {
            "Authorization": f"Bearer {credentials.get('eas_token', None)}" if credentials else None,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    ## External Users Methods
    async def create_external_user(self, email: str, phone: str, name: str) -> CreateExternalUserResponse:
        request = CreateExternalUserRequest(email=email, phone_number=phone, name=name)
        options = RequestOptions(headers=self._eas_headers)
        return await self.client.post(
            endpoint="/authentication-system/v1/users",
            options=options,
            payload=request.model_dump(mode="json", by_alias=True),
            response_model=CreateExternalUserResponse,
        )

    async def get_external_user(self, user_id: str) -> ExternalUserResponse:
        options = RequestOptions(headers=self._eas_headers)

        return await self.client.get(
            endpoint=f"/authentication-system/v1/users/{user_id}",
            options=options,
            response_model=ExternalUserResponse,
        )

    async def update_external_user(self, user_id: str, user_data: UpdateExternalUserRequest) -> UpdateExternalUserResponse:
        options = RequestOptions(headers=self._eas_headers)
        return await self.client.patch(
            endpoint=f"/authentication-system/v1/users/{user_id}",
            options=options,
            payload=user_data.model_dump(mode="json", by_alias=True, exclude_none=True),
            response_model=UpdateExternalUserResponse,
        )

    async def delete_external_user(self, user_id: str) -> None:
        options = RequestOptions(headers=self._eas_headers)
        await self.client.delete(
            endpoint=f"/authentication-system/v1/users/{user_id}",
            options=options,
        )

    async def filter_external_users(
        self,
        id: Optional[str] = None,
        email: Optional[str] = None,
        username: Optional[str] = None,
    ) -> list[ExternalUserResponse]:
        filters = FilterExternalUsersRequest(id=id, email=email, username=username)
        options = RequestOptions(headers=self._eas_headers)
        response = await self.client.get(
            endpoint="/authentication-system/v1/users",
            options=options,
            params=filters.model_dump(mode="json", by_alias=True, exclude_none=True),
            response_model=FilterExternalUsersResponse,
        )
        return response.data

    ## Policy Lifecycle Methods

    async def submit_quotation(self, data: TransmissionData) -> SubmitQuotationResponse:
        payload = SubmitQuotationRequest(data=data)
        return await self.client.post(
            endpoint="/v1/propostas/agricola",
            payload=payload.model_dump(mode="json", by_alias=True),
            response_model=SubmitQuotationResponse,
        )

    async def get_proposal(self, quotation_id: int) -> ProposalStatus:
        payload = GetProposalRequest(quotation_id=quotation_id)
        response = await self.client.get(
            endpoint="/v1/propostas/situacao",
            params=payload.model_dump(mode="json", by_alias=True),
            response_model=GetProposalResponse,
        )
        return response.root[0]

    async def reject_proposal(
        self,
        proposal_id: int,
        description: str,
        motive_code: int,
    ) -> RejectProposalResponse:
        payload = RejectProposalRequest(
            proposal_id=proposal_id,
            description=description,
            motive_code=motive_code,
        )
        return await self.client.post(
            endpoint="/v1/propostas/recusar",
            payload=payload.model_dump(mode="json", by_alias=True),
            response_model=RejectProposalResponse,
        )

    async def issue_policy(self, proposal_id: int) -> IssuePolicyResponse:
        payload = IssuePolicyRequest(proposal_id=proposal_id)
        return await self.client.post(
            endpoint="/v1/apolices/emitir",
            payload=payload.model_dump(mode="json", by_alias=True),
            response_model=IssuePolicyResponse,
        )

    async def generate_policy_document(
        self,
        proposal_id: int,
        report_type: ReportType = ReportType.PASTURES,
    ) -> PolicyDocumentResponse:
        return await self.client.get(
            endpoint=f"v1/formularios/{proposal_id}/documentos?relatorio_id={report_type}",
            response_model=PolicyDocumentResponse,
        )

    ## Financial Methods

    async def get_installments(
        self,
        proposal_id: str,
        installment: int = 0,
    ) -> InstallmentResponse:
        payload = InstallmentRequest(proposal_id=proposal_id, installment=installment)
        return await self.client.get(
            endpoint="/v1/cobrancas/parcelas/",
            params=payload.model_dump(mode="json", by_alias=True, exclude_none=True),
            response_model=InstallmentResponse,
        )

    async def get_boleto(
        self,
        proposal_id: str,
        installment: int,
    ) -> BoletoResponse:
        payload = BoletoRequest(proposal_id=proposal_id, installment=installment)
        return await self.client.get(
            endpoint="/v1/cobrancas/boletos",
            params=payload.model_dump(mode="json", by_alias=True),
            response_model=BoletoResponse,
        )

    async def get_federal_subsidy_limit(self, cpf_cnpj: str, year: int) -> SubsidyLimitResponse:
        payload = SubsidyLimitRequest(cpf_cnpj=cpf_cnpj, year=year)
        return await self.client.get(
            endpoint="/v1/pessoas/agricultura/subvencao-federal",
            params=payload.model_dump(mode="json", by_alias=True),
            response_model=SubsidyLimitResponse,
        )

    async def cadin_lookup(self, cpf_cnpj: str) -> CadinResponse:
        request = CadinRequest(cpf_cnpj=cpf_cnpj)
        return await self.client.get(
            endpoint="/v1/pessoas/agricultura/cadin",
            params=request.model_dump(mode="json", by_alias=True),
            response_model=CadinResponse,
        )

    ## Lookup Methods

    # Addresses
    async def search_postal_code(
        self,
        postal_code: str,
    ) -> PostalCodeLookupResponse:
        request = PostalCodeLookupRequest(postal_code=postal_code)
        return await self.client.get(
            endpoint=f"/v1/enderecos/{request.postal_code}",
            response_model=PostalCodeLookupResponse,
        )

    async def search_address(
        self,
        city: str,
        state: Optional[str] = None,
        street: Optional[str] = None,
    ) -> AddressLookupResponse:
        request = AddressLookupRequest(state=state, city=city, street=street)
        return await self.client.get(
            endpoint="/v1/enderecos",
            params=request.model_dump(mode="json", by_alias=True, exclude_none=True),
            response_model=AddressLookupResponse,
        )

    # Parties
    async def verify_technical_restriction(self, cpf_cnpj: str) -> TechnicalRestrictionResponse:
        request = TechnicalRestrictionRequest(cpf_cnpj=cpf_cnpj)
        return await self.client.get(
            endpoint=f"/v1/pessoas/{request.cpf_cnpj}/restricao-tecnica",
            response_model=TechnicalRestrictionResponse,
        )

    async def get_natural_person_details(self, cpf: str) -> NaturalPersonResponse:
        request = NaturalPersonRequest(cpf=cpf)
        response = await self.client.get(
            endpoint=f"/v1/pessoas/{request.cpf}/regularidade-pessoa-fisica",
            response_model=PlugNaturalPersonResponse,
        )
        return NaturalPersonResponse(
            cpf=response.cpf,
            birth_date=response.birth_date,
            name=response.person_info.name,
            status=response.person_info.status,
        )

    async def get_legal_entity_details(self, cnpj: str) -> LegalEntityResponse:
        request = LegalEntityRequest(cnpj=cnpj)
        response = await self.client.get(
            endpoint=f"/v1/pessoas/{request.cnpj}/regularidade-pessoa-juridica",
            response_model=PlugLegalEntityResponse,
        )
        return LegalEntityResponse(
            cnpj=response.cnpj,
            trade_name=response.legal_entity.name,
            registration_date=response.legal_entity.registration_info.date,
            status=response.legal_entity.registration_info.status,
        )

    async def get_broker_details(self, cpf_cnpj: str) -> BrokerResponse:
        request = BrokerRequest(cpf_cnpj=cpf_cnpj)
        return await self.client.get(
            endpoint=f"/v1/pessoas/corretores/{request.cpf_cnpj}",
            response_model=BrokerResponse,
        )

    ## Notification Methods

    async def send_email(
        self,
        application: Applications,
        template: EmailTemplateTypes,
        subject: str,
        description: str,
        body: list[dict[str, str]],
        to: list[dict[str, str]],
        product_code: Optional[ProductCodes] = None,
        cc: Optional[list[dict[str, str]]] = None,
        bcc: Optional[list[dict[str, str]]] = None,
        quotation_number: Optional[str] = None,
        proposal_number: Optional[str] = None,
        policy_number: Optional[str] = None,
        proposal_id: Optional[str] = None,
        attachments: Optional[list[dict[str, str]]] = None,
    ) -> EmailNotificationResponse:
        request = EmailNotificationRequest(
            application=application,
            template_type=template,
            to=[Recipient(**recipient) for recipient in to],
            cc=[Recipient(**recipient) for recipient in cc] if cc else None,
            bcc=[Recipient(**recipient) for recipient in bcc] if bcc else None,
            subject=subject,
            description=description,
            body=[Content(**content) for content in body],
            product_code=product_code,
            quotation_number=quotation_number,
            proposal_number=proposal_number,
            policy_number=policy_number,
            proposal_id=int(proposal_id) if proposal_id else None,
            attachments=[Attachments(**attachment) for attachment in attachments] if attachments else None,
        )
        return await self.client.post(
            endpoint="/v1/notificacoes",
            response_model=EmailNotificationResponse,
            payload=request.model_dump(mode="json", by_alias=True, exclude_none=True),
        )
