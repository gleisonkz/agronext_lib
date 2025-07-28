from typing import Optional
from .async_client import BaseAsyncClient
from .legal_entity.schemas import (
    IndividualRequest,
    IndividualResponse,
    CompanyRequest,
    CompanyResponse,
)

from .policy.schemas import (
    TransmissionRequest,
    TransmissionResponse,
    RejectProposalRequest,
    IssuePolicyRequest,
    InstallmentRequest,
    InstallmentResponse,
    BoletoRequest,
    BoletoResponse,
    SubsidyLimitRequest,
    SubsidyLimitResponse,
)
from .validations.schemas import (
    AddressLookupRequest,
    AddressLookupResponse,
    TechnicalRestrictionRequest,
    TechnicalRestrictionResponse,
)


class PlugSDK:
    def __init__(
        self,
        base_url: str,
        credentials: dict | None = None,
        headers: Optional[dict[str, str]] = None,
    ):
        self.client = BaseAsyncClient(base_url=base_url, headers=headers)
        self.credentials = credentials

    ## Procurement Methods

    async def transmit_quotation(
        self, data: TransmissionRequest
    ) -> TransmissionResponse:
        return await self.client.post(
            endpoint="/propostas/agro",
            payload=data.model_dump(mode="json", by_alias=True),
            response_model=TransmissionResponse,
        )

    async def reject_proposal(
        self, data: RejectProposalRequest
    ) -> TransmissionResponse:
        return await self.client.post(
            endpoint="/propostas/agro/recusar",
            payload=data.model_dump(mode="json", by_alias=True),
            response_model=TransmissionResponse,
        )

    async def issue_policy(self, data: IssuePolicyRequest) -> TransmissionResponse:
        return await self.client.post(
            endpoint="/apolices/agro",
            payload=data.model_dump(mode="json", by_alias=True),
            response_model=TransmissionResponse,
        )

    async def get_subsidy_limit(
        self, request: SubsidyLimitRequest
    ) -> SubsidyLimitResponse:
        return await self.client.get(
            endpoint="/v1/mapa/limite-financeiro",
            params={
                "cpfCnpj": request.cpf_cnpj,
                "anoExercicio": request.year,
            },
            response_model=SubsidyLimitResponse,
        )

    async def get_boleto(self, request: BoletoRequest) -> BoletoResponse:
        return await self.client.get(
            endpoint="/boleto",
            params={
                "idEndosso": request.policy_id,
                "numeroParcela": request.installment_number,
            },
            response_model=BoletoResponse,
        )

    async def get_installment(self, request: InstallmentRequest) -> InstallmentResponse:
        return await self.client.get(
            endpoint=f"/v1/parcelas/{request.installment_number}/endosso/{request.policy_id}",
            response_model=InstallmentResponse,
        )

    ## Validation Methods

    async def get_natural_person(
        self, request: IndividualRequest
    ) -> IndividualResponse:
        return await self.client.get(
            endpoint=f"/v1/pessoa/{request.cpf}",
            response_model=IndividualResponse,
        )

    async def get_legal_entity(self, request: CompanyRequest) -> CompanyResponse:
        return await self.client.get(
            endpoint=f"/v1/pessoa/{request.cnpj}",
            response_model=CompanyResponse,
        )

    async def get_address_lookup(
        self, request: AddressLookupRequest
    ) -> AddressLookupResponse:
        return await self.client.get(
            endpoint=f"/cep/v1/enderecos/{request.postal_code}",
            response_model=AddressLookupResponse,
        )

    async def get_technical_restriction(
        self, request: TechnicalRestrictionRequest
    ) -> TechnicalRestrictionResponse:
        url = "http://uatscap.essor.net/api/v1/restricao-tecnica"  # Example URL, replace with actual
        return await self.client.get(
            endpoint=url,
            params={
                "cpfCnpj": request.cpf_cnpj,
                "aplicacao": request.application,
            },
            response_model=TechnicalRestrictionResponse,
        )
