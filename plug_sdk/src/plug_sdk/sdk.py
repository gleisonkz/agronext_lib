from typing import Optional
from .async_client import BaseAsyncClient

from .legal_identity import (
    NaturalPersonRequest,
    NaturalPersonResponse,
    LegalEntityRequest,
    LegalEntityResponse,
    BrokerRequest,
    BrokerResponse,
)

from .financial import (
    InstallmentResponse,
    InstallmentRequest,
    BoletoRequest,
    BoletoResponse,
    SubsidyLimitResponse,
    SubsidyLimitRequest,
    CadinRequest,
    CadinResponse,
)

from .policy import (
    SubmitQuotationRequest,
    SubmitQuotationResponse,
    GetProposalResponse,
    RejectProposalRequest,
    RejectProposalResponse,
    IssuePolicyRequest,
    IssuePolicyResponse,
)
from .validations import (
    AddressLookupRequest,
    PostalCodeLookupRequest,
    AddressLookupResponse,
    TechnicalRestrictionRequest,
    TechnicalRestrictionResponse,
)
from .notifications import EmailNotificationResponse, EmailNotificationRequest
from .gis import (
    GISAllValidationsRequest,
    GISAllValidationsResponse,
)


class PlugSDK:
    def __init__(
        self,
        base_url: str = "http://uatplug.essor.net",
        credentials: dict | None = None,
        headers: Optional[dict[str, str]] = None,
    ):
        self.client = BaseAsyncClient(base_url=base_url, headers=headers)
        self.credentials = credentials

    ## Policy Lifecycle Methods

    async def submit_quotation(
        self, data: SubmitQuotationRequest
    ) -> SubmitQuotationResponse:
        return await self.client.post(
            endpoint="/v1/propostas/agricola",
            payload=data.model_dump(mode="json", by_alias=True),
            response_model=SubmitQuotationResponse,
        )

    async def get_proposal(self, proposal_id: int) -> GetProposalResponse:
        return await self.client.get(
            endpoint="/v1/propostas/situacao",
            params={
                "numeroProposta": proposal_id,
            },
            response_model=GetProposalResponse,
        )

    async def reject_proposal(
        self, data: RejectProposalRequest
    ) -> RejectProposalResponse:
        return await self.client.post(
            endpoint="/v1/propostas/recusar",
            payload=data.model_dump(mode="json", by_alias=True),
            response_model=RejectProposalResponse,
        )

    async def issue_policy(self, request: IssuePolicyRequest) -> IssuePolicyResponse:
        return await self.client.post(
            endpoint="/v1/apolices/emitir",
            payload=request.model_dump(mode="json", by_alias=True),
            response_model=IssuePolicyResponse,
        )

    ## Financial Methods

    async def get_installments(
        self, request: InstallmentRequest
    ) -> InstallmentResponse:
        return await self.client.get(
            endpoint="/v1/cobrancas/parcelas/",
            params=request.model_dump(mode="json", by_alias=True, exclude_none=True),
            response_model=InstallmentResponse,
        )

    async def get_boleto(self, request: BoletoRequest) -> BoletoResponse:
        return await self.client.get(
            endpoint="/v1/cobrancas/boletos",
            params=request.model_dump(mode="json", by_alias=True),
            response_model=BoletoResponse,
        )

    async def get_federal_subsidy_limit(
        self, request: SubsidyLimitRequest
    ) -> SubsidyLimitResponse:
        return await self.client.get(
            endpoint="/v1/pessoas/agricultura/subvencao-federal",
            params=request.model_dump(mode="json", by_alias=True),
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
    ) -> AddressLookupResponse:
        request = PostalCodeLookupRequest(postal_code=postal_code)
        return await self.client.get(
            endpoint=f"/v1/enderecos/{request.postal_code}",
            response_model=AddressLookupResponse,
        )

    async def search_address(
        self,
        state: str,
        city: str,
        street: str,
    ) -> AddressLookupResponse:
        request = AddressLookupRequest(state=state, city=city, street=street)
        return await self.client.get(
            endpoint="/v1/enderecos",
            params=request.model_dump(mode="json", by_alias=True, exclude_none=True),
            response_model=AddressLookupResponse,
        )

    # Parties
    async def get_broker_details(self, cpf_cnpj: str) -> BrokerResponse:
        request = BrokerRequest(cpf_cnpj=cpf_cnpj)
        return await self.client.get(
            endpoint=f"/v1/pessoas/corretores/{request.cpf_cnpj}",
            response_model=BrokerResponse,
        )

    async def get_natural_person_details(self, cpf: str) -> NaturalPersonResponse:
        request = NaturalPersonRequest(cpf=cpf)
        return await self.client.get(
            endpoint=f"/v1/pessoa/{request.cpf}",
            response_model=NaturalPersonResponse,
        )

    async def get_legal_entity_details(self, cnpj: str) -> LegalEntityResponse:
        request = LegalEntityRequest(cnpj=cnpj)
        return await self.client.get(
            endpoint=f"/v1/pessoa/{request.cnpj}",
            response_model=LegalEntityResponse,
        )

    async def verify_technical_restriction(
        self, cpf_cpnj: str
    ) -> TechnicalRestrictionResponse:
        request = TechnicalRestrictionRequest(cpf_cnpj=cpf_cpnj)
        return await self.client.get(
            endpoint=f"/v1/pessoas/{request.cpf_cnpj}/restricao-tecnica",
            response_model=TechnicalRestrictionResponse,
        )

    ## Notification Methods

    async def send_email(
        self, to: str, subject: str, body: EmailNotificationRequest
    ) -> EmailNotificationResponse:
        request = EmailNotificationRequest(
            to=to,
            subject=subject,
            body=body,
        )
        return await self.client.post(
            endpoint="/v1/notificacoes/email",
            response_model=EmailNotificationResponse,
            payload=request.model_dump(mode="json", by_alias=True),
        )

    ## GIS Methods

    async def get_gis_report(
        self,
        polygons: list[list[tuple[float, float]]],
    ) -> str:
        request = GISAllValidationsRequest(polygons)
        return await self.client.post(
            endpoint="/v1/gis/validations/all",
            response_model=GISAllValidationsResponse,
            payload=request.model_dump(mode="json", by_alias=True),
        )
