from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Any, Optional

from ..base_model import BaseModel, Field, RootModel
from .domain_types import (
    DomainAddress,
    DomainAddressDescription,
    DomainBankAccount,
    DomainBankAccountDescription,
    DomainCommunication,
    DomainCommunicationDescription,
    DomainDocument,
    DomainDocumentDescription,
    DomainGender,
    DomainGenderDescription,
    DomainPayment,
    DomainPaymentDescription,
    DomainPerson,
    DomainPersonDescription,
    DomainState,
    DomainStateDescription,
    RoleDescription,
    Roles,
)


class TimeStampMixIn(BaseModel):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class IDMixIn(BaseModel):
    id: Optional[str] = None


class PersonIDMixIn(BaseModel):
    person_id: str


class PartyResponseMixIn(BaseModel):
    party: Optional[PartyResponse] = Field(alias="person", default=None)


class DomainData(BaseModel):
    id: int
    name: str
    code: Optional[str] = None
    active: bool


ListDomainResponse = RootModel[list[DomainData]]


class RoleResponse(BaseModel):
    id: Roles
    name: RoleDescription
    external_id: Optional[int] = None
    note: Optional[str] = None
    has_parameters: bool
    parameters_schema: Optional[dict[str, Any]] = None


ListRolesResponse = RootModel[list[RoleResponse]]


class Address(IDMixIn):
    postal_code: str
    state_id: DomainState = Field(alias="state_type_id")
    country: Optional[str] = None
    city: str
    neighborhood: str = Field(alias="district")
    street: str
    number: str
    complement: Optional[str] = Field(alias="additional_information", default=None)
    address_type: DomainAddress = Field(alias="address_type_id")
    is_primary: bool


class AddressRequest(Address, PersonIDMixIn):
    pass


class AddressResponse(AddressRequest, TimeStampMixIn, PartyResponseMixIn):
    state_description: DomainStateDescription = Field(alias="state_type_description")
    address_description: DomainAddressDescription = Field(alias="address_type_description")


class BankingDetails(IDMixIn):
    bank_number: str
    bank_name: str
    branch_number: int
    branch_check_digit: int
    account_number: int
    account_check_digit: int
    payment_type: DomainPayment = Field(alias="payment_type_id")
    bank_account_type: DomainBankAccount = Field(alias="bank_account_type_id")
    is_active: bool = Field(default=True)
    is_primary: bool = Field(default=True)


class BankingDetailsRequest(BankingDetails, PersonIDMixIn):
    pass


class BankingDetailsResponse(BankingDetailsRequest, TimeStampMixIn, PartyResponseMixIn):
    payment_type_description: DomainPaymentDescription
    bank_account_type_description: DomainBankAccountDescription


class ContactInformation(IDMixIn):
    communication_type: DomainCommunication = Field(alias="communication_type_id")
    description: Optional[str] = None
    contact: str
    observation: Optional[str] = None
    is_primary: bool


class ContactInformationRequest(ContactInformation, PersonIDMixIn):
    pass


class ContactInformationResponse(ContactInformationRequest, TimeStampMixIn, PartyResponseMixIn):
    communication_type_description: DomainCommunicationDescription


class Document(IDMixIn):
    document_type_id: DomainDocument = Field(alias="document_type")
    document_number: Optional[str] = None
    issuing_agency: Optional[str] = None
    issuing_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None


class DocumentRequest(Document, PersonIDMixIn):
    pass


class DocumentResponse(DocumentRequest, TimeStampMixIn, PartyResponseMixIn):
    document_type_description: DomainDocumentDescription


class AssignRoleRequest(BaseModel):
    role_id: int
    attributes: Optional[dict[str, Any]] = None


class AssignRoleResponse(IDMixIn):
    name: str
    attributes: Optional[dict[str, Any]] = None


class Role(BaseModel):
    id: Roles
    name: RoleDescription
    attributes: Optional[dict[str, Any]] = None


class ListPartyRolesResponse(PersonIDMixIn):
    name: str
    roles: list[AssignRoleResponse]


class Party(IDMixIn):
    person_type: DomainPerson = Field(alias="person_type_id")
    full_name: str
    preferred_name: Optional[str] = None
    company_name: Optional[str] = None
    document_number: Optional[str] = None
    birth_date: Optional[datetime] = None
    gender_type: Optional[DomainGender] = Field(alias="gender_type_id", default=None)
    occupation: Optional[str] = None
    monthly_income: Optional[float] = None
    politically_exposed: Optional[bool] = None
    economic_activity: Optional[str] = None
    annual_gross_income: Optional[float] = None
    net_worth: Optional[float] = None
    addresses: list[AddressResponse] = Field(default_factory=list)
    contact_information: list[ContactInformationResponse] = Field(default_factory=list, alias="communications")
    banking_details: list[BankingDetailsResponse] = Field(default_factory=list, alias="bank_accounts")
    documents: list[DocumentResponse] = Field(default_factory=list)
    roles: list[Role] = Field(default_factory=list)


class PartyResponse(Party, TimeStampMixIn):
    person_type_description: Optional[DomainPersonDescription] = None
    gender_type_description: Optional[DomainGenderDescription] = None


## SEARCH AND PAGINATION SCHEMAS


class PaginationLinks(BaseModel):
    first: Optional[str] = None
    last: Optional[str] = None
    prev: Optional[str] = None
    next: Optional[str] = None


class PaginationMetaLinks(BaseModel):
    url: Optional[str] = None
    label: str
    page: Optional[int] = None
    active: bool


class PaginationMeta(BaseModel):
    current_page: int
    from_: Optional[int] = Field(default=None, alias="from")
    last_page: int
    links: Optional[list[PaginationMetaLinks]] = None


class PaginationResponse[T: BaseModel](BaseModel):
    data: list[T] = Field(default_factory=list)
    links: PaginationLinks
    meta: PaginationMeta


class SearchIncludeOptions(StrEnum):
    PARTY = "person"
    ADDRESSES = "addresses"
    CONTACT = "communications"
    BANKING_DETAILS = "bankAccounts"
    DOCUMENTS = "documents"
    ROLES = "roles"


class BaseSearchParams(BaseModel):
    page: Optional[int] = Field(default=1, ge=1, description="Page number for pagination.")
    per_page: Optional[int] = Field(default=10, ge=1, le=100, description="Number of items per page for pagination.")
    include: Optional[list[SearchIncludeOptions]] = Field(
        default=None,
        alias="with[]",
        description="List of related resources to include in the response. "
        "Options: 'person' , 'addresses', 'communications', 'bank_accounts', 'documents', 'roles'.",
    )


class PartySearchParams(BaseSearchParams):
    birth_date: Optional[date] = None
    document_number: Optional[str] = None
    full_name: Optional[str] = None
    gender_type_id: Optional[DomainGender] = None
    person_type_id: Optional[DomainPerson] = None


class PaginatedPartyResponse(PaginationResponse[PartyResponse]):
    pass


class AddressSearchParams(BaseSearchParams):
    party_id: Optional[str] = Field(alias="person_id", default=None)
    postal_code: Optional[str] = None
    address_type_id: Optional[DomainAddress] = None


class PaginatedAddressResponse(PaginationResponse[AddressResponse]):
    pass


class BankingDetailsSearchParams(BaseSearchParams):
    party_id: Optional[str] = Field(alias="person_id", default=None)
    bank_account_type_id: Optional[DomainBankAccount] = None
    payment_type_id: Optional[DomainPayment] = None


class PaginatedBankingDetailsResponse(PaginationResponse[BankingDetailsResponse]):
    pass


class ContactSearchParams(BaseSearchParams):
    party_id: Optional[str] = Field(alias="person_id", default=None)
    communication_type_id: Optional[DomainCommunication] = None
    contact: Optional[str] = None


class PaginatedContactInformationResponse(PaginationResponse[ContactInformationResponse]):
    pass


class DocumentSearchParams(BaseSearchParams):
    party_id: Optional[str] = Field(alias="person_id", default=None)
    document_type_id: Optional[DomainDocument] = None
    issuing_agency: Optional[str] = None
    document_number: Optional[str] = None


class PaginatedDocumentResponse(PaginationResponse[DocumentResponse]):
    pass
