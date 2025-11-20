from datetime import date
from typing import Optional

from .async_client import URL, BaseAsyncClient, RequestOptions
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
    CadinPlugResponse,
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
from .scap import (
    Address,
    AddressRequest,
    AddressResponse,
    AddressSearchParams,
    AssignRoleRequest,
    AssignRoleResponse,
    BankingDetails,
    BankingDetailsRequest,
    BankingDetailsResponse,
    BankingDetailsSearchParams,
    ContactInformation,
    ContactInformationRequest,
    ContactInformationResponse,
    ContactSearchParams,
    Document,
    DocumentRequest,
    DocumentResponse,
    DocumentSearchParams,
    DomainTypes,
    ListDomainResponse,
    ListPartyRolesResponse,
    ListRolesResponse,
    PaginatedAddressResponse,
    PaginatedBankingDetailsResponse,
    PaginatedContactInformationResponse,
    PaginatedDocumentResponse,
    PaginatedPartyResponse,
    Party,
    PartyResponse,
    PartySearchParams,
    SearchIncludeOptions,
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
        timeout: float = 60.0,
    ):
        default_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {credentials.get('api_key', '')}"
            if credentials
            else "",
            "External-User-Id": credentials.get("external_user_id", "")
            if credentials
            else "",
        }
        headers = default_headers.update(headers) if headers else default_headers

        self.client = BaseAsyncClient(
            base_url=URL(base_url), headers=headers, timeout=timeout
        )

    ## External Users Methods
    async def create_external_user(
        self, email: str, phone: str, name: str
    ) -> CreateExternalUserResponse:
        request = CreateExternalUserRequest(email=email, phone_number=phone, name=name)
        return await self.client.post(
            endpoint="/authentication-system/v1/users",
            payload=request.model_dump(mode="json", by_alias=True),
            response_model=CreateExternalUserResponse,
        )

    async def get_external_user(self, user_id: str) -> ExternalUserResponse:
        return await self.client.get(
            endpoint=f"/authentication-system/v1/users/{user_id}",
            response_model=ExternalUserResponse,
        )

    async def update_external_user(
        self, user_id: str, user_data: UpdateExternalUserRequest
    ) -> UpdateExternalUserResponse:
        return await self.client.patch(
            endpoint=f"/authentication-system/v1/users/{user_id}",
            payload=user_data.model_dump(mode="json", by_alias=True, exclude_none=True),
            response_model=UpdateExternalUserResponse,
        )

    async def delete_external_user(self, user_id: str) -> None:
        await self.client.delete(
            endpoint=f"/authentication-system/v1/users/{user_id}",
        )

    async def filter_external_users(
        self,
        id: Optional[str] = None,
        email: Optional[str] = None,
        username: Optional[str] = None,
    ) -> list[ExternalUserResponse]:
        filters = FilterExternalUsersRequest(id=id, email=email, username=username)
        response = await self.client.get(
            endpoint="/authentication-system/v1/users",
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

    async def get_federal_subsidy_limit(
        self, cpf_cnpj: str, year: int
    ) -> SubsidyLimitResponse:
        payload = SubsidyLimitRequest(cpf_cnpj=cpf_cnpj, year=year)
        return await self.client.get(
            endpoint="/v1/pessoas/agricultura/subvencao-federal",
            params=payload.model_dump(mode="json", by_alias=True),
            response_model=SubsidyLimitResponse,
        )

    async def cadin_lookup(self, cpf_cnpj: str) -> CadinResponse:
        request = CadinRequest(cpf_cnpj=cpf_cnpj)
        response = await self.client.get(
            endpoint="/v1/pessoas/agricultura/cadin",
            params=request.model_dump(mode="json", by_alias=True),
            response_model=CadinPlugResponse,
        )
        return CadinResponse.from_plug_response(response)

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
    async def verify_technical_restriction(
        self, cpf_cnpj: str
    ) -> TechnicalRestrictionResponse:
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
            attachments=[Attachments(**attachment) for attachment in attachments]
            if attachments
            else None,
        )
        return await self.client.post(
            endpoint="/v1/notificacoes",
            response_model=EmailNotificationResponse,
            payload=request.model_dump(mode="json", by_alias=True, exclude_none=True),
        )

    ## SCAP METHODS

    #
    async def list_domain_items(self, domain: DomainTypes | str) -> ListDomainResponse:
        """List all active items for a given domain"""
        param = domain.value if isinstance(domain, DomainTypes) else domain
        return await self.client.get(
            endpoint=f"/unified-person-registry/v1/domains/{param}",
            response_model=ListDomainResponse,
        )

    async def list_roles(self) -> ListRolesResponse:
        """Retrieve all available roles
        id = 1: Corretor
        id = 2: Cliente
        id = 3: Beneficiário
        id = 4: Vistoriador
        id = 5: Perito
        """
        return await self.client.get(
            endpoint="/unified-person-registry/v1/roles",
            response_model=ListRolesResponse,
        )

    #
    async def create_party(self, payload: Party) -> PartyResponse:
        """Create a new person with all related details"""
        return await self.client.post(
            endpoint="/unified-person-registry/v1/people/with-details",
            payload=payload.model_dump(mode="json", by_alias=True, exclude_none=True),
            response_model=PartyResponse,
        )

    async def get_party(self, id: str) -> PartyResponse:
        """Retrieve person by ID"""
        return await self.client.get(
            endpoint=f"/unified-person-registry/v1/people/{id}",
            response_model=PartyResponse,
        )

    async def update_party(
        self,
        person_id: str,
        payload: Party,
    ) -> PartyResponse:
        """Update an existing person"""

        return await self.client.put(
            endpoint=f"/unified-person-registry/v1/people/{person_id}",
            payload=payload.model_dump(mode="json", by_alias=True),
            response_model=PartyResponse,
        )

    async def assign_role(
        self, person_id: str, payload: AssignRoleRequest
    ) -> AssignRoleResponse:
        """Assign a role to a person"""

        return await self.client.post(
            endpoint=f"/unified-person-registry/v1/people/{person_id}/assign-role",
            payload=payload.model_dump(mode="json", by_alias=True),
            response_model=AssignRoleResponse,
        )

    async def get_party_roles(self, id: str) -> ListPartyRolesResponse:
        """Get roles assigned to a person"""
        return await self.client.get(
            endpoint=f"/unified-person-registry/v1/people/{id}/roles",
            response_model=ListPartyRolesResponse,
        )

    #
    async def register_address(self, payload: AddressRequest) -> AddressResponse:
        """Register a new address to a party"""

        return await self.client.post(
            endpoint="/unified-person-registry/v1/people/addresses",
            payload=payload.model_dump(mode="json", by_alias=True),
            response_model=AddressResponse,
        )

    async def get_address(self, id: str) -> AddressResponse:
        """Retrieve address by ID"""
        return await self.client.get(
            endpoint=f"/unified-person-registry/v1/people/addresses/{id}",
            response_model=AddressResponse,
        )

    async def update_address(self, id: str, payload: Address) -> AddressResponse:
        """Update an existing address"""

        return await self.client.put(
            endpoint=f"/unified-person-registry/v1/people/addresses/{id}",
            payload=payload.model_dump(mode="json", by_alias=True),
            response_model=AddressResponse,
        )

    #
    async def register_bank_account(
        self, payload: BankingDetailsRequest
    ) -> BankingDetailsResponse:
        """Create a new bank account"""

        return await self.client.post(
            endpoint="/unified-person-registry/v1/people/bank-accounts",
            payload=payload.model_dump(mode="json", by_alias=True),
            response_model=BankingDetailsResponse,
        )

    async def get_bank_account(self, id: str) -> BankingDetailsResponse:
        """Retrieve bank account by ID"""
        return await self.client.get(
            endpoint=f"/unified-person-registry/v1/people/bank-accounts/{id}",
            response_model=BankingDetailsResponse,
        )

    async def update_bank_account(
        self, id: str, payload: BankingDetails
    ) -> BankingDetailsResponse:
        """Update an existing bank account"""

        return await self.client.put(
            endpoint=f"/unified-person-registry/v1/people/bank-accounts/{id}",
            payload=payload.model_dump(mode="json", by_alias=True),
            response_model=BankingDetailsResponse,
        )

    #
    async def register_contact_information(
        self, payload: ContactInformationRequest
    ) -> ContactInformationResponse:
        """Create a new communication"""

        return await self.client.post(
            endpoint="/unified-person-registry/v1/people/communications",
            payload=payload.model_dump(mode="json", by_alias=True),
            response_model=ContactInformationResponse,
        )

    async def get_contact_information(self, id: str) -> ContactInformationResponse:
        """Retrieve communication by ID"""
        return await self.client.get(
            endpoint=f"/unified-person-registry/v1/people/communications/{id}",
            response_model=ContactInformationResponse,
        )

    async def update_contact_information(
        self, id: str, payload: ContactInformation
    ) -> ContactInformationResponse:
        """Update an existing communication"""

        return await self.client.put(
            endpoint=f"/unified-person-registry/v1/people/communications/{id}",
            payload=payload.model_dump(mode="json", by_alias=True),
            response_model=ContactInformationResponse,
        )

    #
    async def register_document(self, payload: DocumentRequest) -> DocumentResponse:
        """Create a new document"""

        return await self.client.post(
            endpoint="/unified-person-registry/v1/people/documents",
            payload=payload.model_dump(mode="json", by_alias=True),
            response_model=DocumentResponse,
        )

    async def get_document(self, id: str) -> DocumentResponse:
        """Retrieve document by ID"""
        return await self.client.get(
            endpoint=f"/unified-person-registry/v1/people/documents/{id}",
            response_model=DocumentResponse,
        )

    async def update_document(
        self, document_id: str, payload: Document
    ) -> DocumentResponse:
        """Update an existing document"""

        return await self.client.put(
            endpoint=f"/unified-person-registry/v1/people/documents/{document_id}",
            payload=payload.model_dump(mode="json", by_alias=True),
            response_model=DocumentResponse,
        )

    #
    async def list_parties(
        self,
        full_name: Optional[str] = None,
        birth_date: Optional[date] = None,
        document_number: Optional[str] = None,
        person_type_id: Optional[int] = None,
        gender_type_id: Optional[int] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        include: Optional[list[SearchIncludeOptions]] = None,
    ) -> PaginatedPartyResponse:
        """Retrieve paginated list of people"""
        params = PartySearchParams(
            birth_date=birth_date,
            full_name=full_name,
            document_number=document_number,
            person_type_id=person_type_id,
            gender_type_id=gender_type_id,
            page=page,
            per_page=per_page,
            include=[i for i in include if i is not SearchIncludeOptions.PARTY]
            if include
            else None,
        )

        return await self.client.get(
            endpoint="/unified-person-registry/v1/people",
            params=params.model_dump(mode="json", by_alias=True, exclude_none=True),
            response_model=PaginatedPartyResponse,
        )

    async def list_addresses(
        self,
        person_id: Optional[str] = None,
        postal_code: Optional[str] = None,
        address_type_id: Optional[int] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        include_person: bool = True,
    ) -> PaginatedAddressResponse:
        """Retrieve paginated list of addresses"""
        params = AddressSearchParams(
            person_id=person_id,
            postal_code=postal_code,
            address_type_id=address_type_id,
            page=page,
            per_page=per_page,
            include=[SearchIncludeOptions.PARTY] if include_person else None,
        )

        return await self.client.get(
            endpoint="/unified-person-registry/v1/people/addresses",
            params=params.model_dump(mode="json", by_alias=True, exclude_none=True),
            response_model=PaginatedAddressResponse,
        )

    async def list_bank_details(
        self,
        person_id: Optional[str] = None,
        bank_account_type_id: Optional[int] = None,
        payment_type_id: Optional[int] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        include_person: bool = True,
    ) -> PaginatedBankingDetailsResponse:
        """Retrieve paginated list of bank accounts"""
        params = BankingDetailsSearchParams(
            person_id=person_id,
            bank_account_type_id=bank_account_type_id,
            payment_type_id=payment_type_id,
            page=page,
            per_page=per_page,
            include=[SearchIncludeOptions.PARTY] if include_person else None,
        )

        return await self.client.get(
            endpoint="/unified-person-registry/v1/people/bank-accounts",
            params=params.model_dump(mode="json", by_alias=True, exclude_none=True),
            response_model=PaginatedBankingDetailsResponse,
        )

    async def list_contact_information(
        self,
        person_id: Optional[str] = None,
        contact_type_id: Optional[int] = None,
        is_primary: Optional[bool] = None,
        contact: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        include_person: bool = True,
    ) -> PaginatedContactInformationResponse:
        """Retrieve paginated list of communications"""
        params = ContactSearchParams(
            person_id=person_id,
            communication_type_id=contact_type_id,
            is_primary=is_primary,
            contact=contact,
            page=page,
            per_page=per_page,
            include=[SearchIncludeOptions.PARTY] if include_person else None,
        )

        return await self.client.get(
            endpoint="/unified-person-registry/v1/people/communications",
            params=params.model_dump(mode="json", by_alias=True, exclude_none=True),
            response_model=PaginatedContactInformationResponse,
        )

    async def list_documents(
        self,
        person_id: Optional[str] = None,
        document_number: Optional[str] = None,
        document_type_id: Optional[int] = None,
        issuing_agency: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        include_person: bool = True,
    ) -> PaginatedDocumentResponse:
        """Retrieve paginated list of documents"""
        params = DocumentSearchParams(
            person_id=person_id,
            document_number=document_number,
            document_type_id=document_type_id,
            issuing_agency=issuing_agency,
            page=page,
            per_page=per_page,
            include=[SearchIncludeOptions.PARTY] if include_person else None,
        )

        return await self.client.get(
            endpoint="/unified-person-registry/v1/people/documents",
            params=params.model_dump(mode="json", by_alias=True, exclude_none=True),
            response_model=PaginatedDocumentResponse,
        )
