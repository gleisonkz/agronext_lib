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
from .scap import (
    Address,
    AddressRequest,
    AddressResponse,
    AssignRoleRequest,
    AssignRoleResponse,
    BankingDetails,
    BankingDetailsRequest,
    BankingDetailsResponse,
    ContactInformation,
    ContactInformationRequest,
    ContactInformationResponse,
    Document,
    DocumentRequest,
    DocumentResponse,
    DomainListResponse,
    DomainTypes,
    ListPartyRolesResponse,
    ListRolesResponse,
    Party,
    PartyResponse,
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
        headers = headers or {
            "Authorization": f"Bearer {credentials.get('api_key', None)}" if credentials else None,
            "Content-Type": "application/json",
            "Accept": "application/json",
            #   --header 'External-User-Id: usr_12345' \
        }
        self.client = BaseAsyncClient(base_url=base_url, headers=headers)

    ## External Users Methods
    async def create_external_user(self, email: str, phone: str, name: str) -> CreateExternalUserResponse:
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

    async def update_external_user(self, user_id: str, user_data: UpdateExternalUserRequest) -> UpdateExternalUserResponse:
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

    ## SCAP METHODS

    # -------------------------------------------------------
    # GET /v1/domains/{domain}
    # -------------------------------------------------------
    async def list_domain_items(self, domain: DomainTypes | str) -> DomainListResponse:
        """List all active items for a given domain"""
        param = domain.value if isinstance(domain, DomainTypes) else domain
        return await self.client.get(
            endpoint=f"/unified-person-registry/v1/domains/{param}",
            response_model=DomainListResponse,
        )

    # -------------------------------------------------------
    # GET /v1/roles
    # -------------------------------------------------------
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

    # # -------------------------------------------------------
    # # GET /v1/people/addresses
    # # -------------------------------------------------------
    # async def list_addresses(
    #     self,
    #     per_page: Optional[int] = None,
    #     person_id: Optional[str] = None,
    #     address_type_id: Optional[int] = None,
    #     postal_code: Optional[str] = None,
    #     with_: Optional[list[str]] = None,
    # ) -> PaginatedAddressesResponse:
    #     """Retrieve paginated list of addresses"""
    #     params = AddressQueryParams(
    #         per_page=per_page,
    #         person_id=person_id,
    #         address_type_id=address_type_id,
    #         postal_code=postal_code,
    #         with_=with_,
    #     ).model_dump(mode="json", by_alias=True)

    #     return await self.client.get(
    #         endpoint="/v1/people/addresses",
    #         params=params,
    #         response_model=PaginatedAddressesResponse,
    #     )

    # # -------------------------------------------------------
    # # POST /v1/people/addresses
    # # -------------------------------------------------------
    # async def create_address(
    #     self,
    #     data: StoreAddressRequest,
    #     external_user_id: str,
    # ) -> CreateAddressResponse:
    #     """Create a new address"""
    #     payload = StoreAddressRequest(**data.model_dump())
    #     headers = {"External-User-Id": external_user_id}

    #     return await self.client.post(
    #         endpoint="/v1/people/addresses",
    #         headers=headers,
    #         payload=payload.model_dump(mode="json", by_alias=True),
    #         response_model=CreateAddressResponse,
    #     )

    # # -------------------------------------------------------
    # # GET /v1/people/addresses/{id}
    # # -------------------------------------------------------
    # async def get_address(self, id: str) -> GetAddressResponse:
    #     """Retrieve address by ID"""
    #     return await self.client.get(
    #         endpoint=f"/v1/people/addresses/{id}",
    #         response_model=GetAddressResponse,
    #     )

    # # -------------------------------------------------------
    # # PUT /v1/people/addresses/{address}
    # # -------------------------------------------------------
    # async def update_address(
    #     self,
    #     address_id: str,
    #     data: UpdateAddressRequest,
    #     external_user_id: str,
    # ) -> UpdateAddressResponse:
    #     """Update an existing address"""
    #     payload = UpdateAddressRequest(**data.model_dump(exclude_none=True))
    #     headers = {"External-User-Id": external_user_id}

    #     return await self.client.put(
    #         endpoint=f"/v1/people/addresses/{address_id}",
    #         headers=headers,
    #         payload=payload.model_dump(mode="json", by_alias=True),
    #         response_model=UpdateAddressResponse,
    #     )

    # # -------------------------------------------------------
    # # GET /v1/people/bank-accounts
    # # -------------------------------------------------------
    # async def list_bank_accounts(
    #     self,
    #     per_page: Optional[int] = None,
    #     person_id: Optional[str] = None,
    #     payment_type_id: Optional[int] = None,
    #     bank_account_type_id: Optional[int] = None,
    #     with_: Optional[list[str]] = None,
    # ) -> PaginatedBankAccountsResponse:
    #     """Retrieve paginated list of bank accounts"""
    #     params = BankAccountQueryParams(
    #         per_page=per_page,
    #         person_id=person_id,
    #         payment_type_id=payment_type_id,
    #         bank_account_type_id=bank_account_type_id,
    #         with_=with_,
    #     ).model_dump(mode="json", by_alias=True)

    #     return await self.client.get(
    #         endpoint="/v1/people/bank-accounts",
    #         params=params,
    #         response_model=PaginatedBankAccountsResponse,
    #     )

    # # -------------------------------------------------------
    # # POST /v1/people/bank-accounts
    # # -------------------------------------------------------
    # async def create_bank_account(
    #     self,
    #     data: StoreBankAccountRequest,
    #     external_user_id: str,
    # ) -> CreateBankAccountResponse:
    #     """Create a new bank account"""
    #     payload = StoreBankAccountRequest(**data.model_dump())
    #     headers = {"External-User-Id": external_user_id}

    #     return await self.client.post(
    #         endpoint="/v1/people/bank-accounts",
    #         headers=headers,
    #         payload=payload.model_dump(mode="json", by_alias=True),
    #         response_model=CreateBankAccountResponse,
    #     )

    # # -------------------------------------------------------
    # # GET /v1/people/bank-accounts/{id}
    # # -------------------------------------------------------
    # async def get_bank_account(self, id: str) -> GetBankAccountResponse:
    #     """Retrieve bank account by ID"""
    #     return await self.client.get(
    #         endpoint=f"/v1/people/bank-accounts/{id}",
    #         response_model=GetBankAccountResponse,
    #     )

    # # -------------------------------------------------------
    # # PUT /v1/people/bank-accounts/{bankAccount}
    # # -------------------------------------------------------
    # async def update_bank_account(
    #     self,
    #     bank_account_id: str,
    #     data: UpdateBankAccountRequest,
    #     external_user_id: str,
    # ) -> UpdateBankAccountResponse:
    #     """Update an existing bank account"""
    #     payload = UpdateBankAccountRequest(**data.model_dump(exclude_none=True))
    #     headers = {"External-User-Id": external_user_id}

    #     return await self.client.put(
    #         endpoint=f"/v1/people/bank-accounts/{bank_account_id}",
    #         headers=headers,
    #         payload=payload.model_dump(mode="json", by_alias=True),
    #         response_model=UpdateBankAccountResponse,
    #     )

    # # -------------------------------------------------------
    # # GET /v1/people/communications
    # # -------------------------------------------------------
    # async def list_communications(
    #     self,
    #     per_page: Optional[int] = None,
    #     person_id: Optional[str] = None,
    #     contact: Optional[str] = None,
    #     communication_type_id: Optional[int] = None,
    #     is_primary: Optional[bool] = None,
    #     with_: Optional[list[str]] = None,
    # ) -> PaginatedCommunicationsResponse:
    #     """Retrieve paginated list of communications"""
    #     params = CommunicationQueryParams(
    #         per_page=per_page,
    #         person_id=person_id,
    #         contact=contact,
    #         communication_type_id=communication_type_id,
    #         is_primary=is_primary,
    #         with_=with_,
    #     ).model_dump(mode="json", by_alias=True)

    #     return await self.client.get(
    #         endpoint="/v1/people/communications",
    #         params=params,
    #         response_model=PaginatedCommunicationsResponse,
    #     )

    # # -------------------------------------------------------
    # # POST /v1/people/communications
    # # -------------------------------------------------------
    # async def create_communication(
    #     self,
    #     data: StoreCommunicationRequest,
    #     external_user_id: str,
    # ) -> CreateCommunicationResponse:
    #     """Create a new communication"""
    #     payload = StoreCommunicationRequest(**data.model_dump())
    #     headers = {"External-User-Id": external_user_id}

    #     return await self.client.post(
    #         endpoint="/v1/people/communications",
    #         headers=headers,
    #         payload=payload.model_dump(mode="json", by_alias=True),
    #         response_model=CreateCommunicationResponse,
    #     )

    # # -------------------------------------------------------
    # # GET /v1/people/communications/{id}
    # # -------------------------------------------------------
    # async def get_communication(self, id: str) -> GetCommunicationResponse:
    #     """Retrieve communication by ID"""
    #     return await self.client.get(
    #         endpoint=f"/v1/people/communications/{id}",
    #         response_model=GetCommunicationResponse,
    #     )

    # # -------------------------------------------------------
    # # PUT /v1/people/communications/{communication}
    # # -------------------------------------------------------
    # async def update_communication(
    #     self,
    #     communication_id: str,
    #     data: UpdateCommunicationRequest,
    #     external_user_id: str,
    # ) -> UpdateCommunicationResponse:
    #     """Update an existing communication"""
    #     payload = UpdateCommunicationRequest(**data.model_dump(exclude_none=True))
    #     headers = {"External-User-Id": external_user_id}

    #     return await self.client.put(
    #         endpoint=f"/v1/people/communications/{communication_id}",
    #         headers=headers,
    #         payload=payload.model_dump(mode="json", by_alias=True),
    #         response_model=UpdateCommunicationResponse,
    #     )

    # # -------------------------------------------------------
    # # GET /v1/people/documents
    # # -------------------------------------------------------
    # async def list_documents(
    #     self,
    #     per_page: Optional[int] = None,
    #     person_id: Optional[str] = None,
    #     document_type_id: Optional[int] = None,
    #     document_number: Optional[str] = None,
    #     issuing_agency: Optional[str] = None,
    #     with_: Optional[list[str]] = None,
    # ) -> PaginatedDocumentsResponse:
    #     """Retrieve paginated list of documents"""
    #     params = DocumentQueryParams(
    #         per_page=per_page,
    #         person_id=person_id,
    #         document_type_id=document_type_id,
    #         document_number=document_number,
    #         issuing_agency=issuing_agency,
    #         with_=with_,
    #     ).model_dump(mode="json", by_alias=True)

    #     return await self.client.get(
    #         endpoint="/v1/people/documents",
    #         params=params,
    #         response_model=PaginatedDocumentsResponse,
    #     )

    # # -------------------------------------------------------
    # # POST /v1/people/documents
    # # -------------------------------------------------------
    # async def create_document(
    #     self,
    #     data: StoreDocumentRequest,
    #     external_user_id: str,
    # ) -> CreateDocumentResponse:
    #     """Create a new document"""
    #     payload = StoreDocumentRequest(**data.model_dump())
    #     headers = {"External-User-Id": external_user_id}

    #     return await self.client.post(
    #         endpoint="/v1/people/documents",
    #         headers=headers,
    #         payload=payload.model_dump(mode="json", by_alias=True),
    #         response_model=CreateDocumentResponse,
    #     )

    # # -------------------------------------------------------
    # # GET /v1/people/documents/{id}
    # # -------------------------------------------------------
    # async def get_document(self, id: str) -> GetDocumentResponse:
    #     """Retrieve document by ID"""
    #     return await self.client.get(
    #         endpoint=f"/v1/people/documents/{id}",
    #         response_model=GetDocumentResponse,
    #     )

    # # -------------------------------------------------------
    # # PUT /v1/people/documents/{document}
    # # -------------------------------------------------------
    # async def update_document(
    #     self,
    #     document_id: str,
    #     data: UpdateDocumentRequest,
    #     external_user_id: str,
    # ) -> UpdateDocumentResponse:
    #     """Update an existing document"""
    #     payload = UpdateDocumentRequest(**data.model_dump(exclude_none=True))
    #     headers = {"External-User-Id": external_user_id}

    #     return await self.client.put(
    #         endpoint=f"/v1/people/documents/{document_id}",
    #         headers=headers,
    #         payload=payload.model_dump(mode="json", by_alias=True),
    #         response_model=UpdateDocumentResponse,
    #     )

    # # -------------------------------------------------------
    # # GET /v1/people
    # # -------------------------------------------------------
    # async def list_people(
    #     self,
    #     per_page: Optional[int] = None,
    #     full_name: Optional[str] = None,
    #     document_number: Optional[str] = None,
    #     person_type_id: Optional[int] = None,
    #     gender_type_id: Optional[int] = None,
    #     with_: Optional[list[str]] = None,
    # ) -> PaginatedPersonsResponse:
    #     """Retrieve paginated list of people"""
    #     params = PersonQueryParams(
    #         per_page=per_page,
    #         full_name=full_name,
    #         document_number=document_number,
    #         person_type_id=person_type_id,
    #         gender_type_id=gender_type_id,
    #         with_=with_,
    #     ).model_dump(mode="json", by_alias=True)

    #     return await self.client.get(
    #         endpoint="/v1/people",
    #         params=params,
    #         response_model=PaginatedPersonsResponse,
    #     )

    # # -------------------------------------------------------
    # # POST /v1/people/with-details
    # # -------------------------------------------------------
    # async def create_person_with_details(
    #     self,
    #     data: StorePersonWithDetailsRequest,
    #     external_user_id: str,
    # ) -> CreatePersonWithDetailsResponse:
    #     """Create a new person with all related details"""
    #     payload = StorePersonWithDetailsRequest(**data.model_dump())
    #     headers = {"External-User-Id": external_user_id}

    #     return await self.client.post(
    #         endpoint="/v1/people/with-details",
    #         headers=headers,
    #         payload=payload.model_dump(mode="json", by_alias=True),
    #         response_model=CreatePersonWithDetailsResponse,
    #     )

    # # -------------------------------------------------------
    # # GET /v1/people/{id}
    # # -------------------------------------------------------
    # async def get_person(self, id: str) -> GetPersonResponse:
    #     """Retrieve person by ID"""
    #     return await self.client.get(
    #         endpoint=f"/v1/people/{id}",
    #         response_model=GetPersonResponse,
    #     )

    # # -------------------------------------------------------
    # # PUT /v1/people/{person}
    # # -------------------------------------------------------
    # async def update_person(
    #     self,
    #     person_id: str,
    #     data: UpdatePersonRequest,
    #     external_user_id: str,
    # ) -> UpdatePersonResponse:
    #     """Update an existing person"""
    #     payload = UpdatePersonRequest(**data.model_dump(exclude_none=True))
    #     headers = {"External-User-Id": external_user_id}

    #     return await self.client.put(
    #         endpoint=f"/v1/people/{person_id}",
    #         headers=headers,
    #         payload=payload.model_dump(mode="json", by_alias=True),
    #         response_model=UpdatePersonResponse,
    #     )

    # # -------------------------------------------------------
    # # POST /v1/people/{id}/assign-role
    # # -------------------------------------------------------
    # async def assign_role(
    #     self,
    #     person_id: str,
    #     data: AssignPersonRoleRequest,
    #     external_user_id: str,
    # ) -> PersonRoleResponse:
    #     """Assign a role to a person"""
    #     payload = AssignPersonRoleRequest(**data.model_dump(exclude_none=True))
    #     headers = {"External-User-Id": external_user_id}

    #     return await self.client.post(
    #         endpoint=f"/v1/people/{person_id}/assign-role",
    #         headers=headers,
    #         payload=payload.model_dump(mode="json", by_alias=True),
    #         response_model=PersonRoleResponse,
    #     )

    # # -------------------------------------------------------
    # # GET /v1/people/{id}/roles
    # # -------------------------------------------------------
    # async def get_person_roles(self, id: str) -> PersonRolesResponse:
    #     """Get roles assigned to a person"""
    #     return await self.client.get(
    #         endpoint=f"/v1/people/{id}/roles",
    #         response_model=PersonRolesResponse,
    #     )
