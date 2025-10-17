from datetime import date, datetime
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


class TimeStampMixin(BaseModel):
    created_at: datetime
    updated_at: datetime


class IDMixin(BaseModel):
    person_id: str


class PersonIDMixin(BaseModel):
    person_id: str


class DomainData(BaseModel):
    id: int
    name: str
    code: Optional[str] = None
    active: bool


DomainListResponse = RootModel[list[DomainData]]


class RoleResponse(BaseModel):
    id: Roles
    name: RoleDescription
    external_id: Optional[int] = None
    note: Optional[str] = None
    has_parameters: bool
    parameters_schema: Optional[dict[str, Any]] = None


ListRolesResponse = RootModel[list[RoleResponse]]


class Address(BaseModel):
    postal_code: str
    state_id: DomainState = Field(alias="state_type_id")
    country: str
    city: str
    neighborhood: str = Field(alias="district")
    street: str
    number: str
    complement: Optional[str] = Field(alias="additional_information", default=None)
    address_type: DomainAddress = Field(alias="address_type_id")
    is_primary: bool


class AddressRequest(Address, PersonIDMixin):
    pass


class AddressResponse(Address, IDMixin, PersonIDMixin, TimeStampMixin):
    state_description: DomainStateDescription = Field(alias="state_type_description")
    address_description: DomainAddressDescription = Field(alias="address_type_description")


class BankingDetails(BaseModel):
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


class BankingDetailsRequest(BankingDetails, PersonIDMixin):
    pass


class BankingDetailsResponse(BankingDetails, IDMixin, PersonIDMixin, TimeStampMixin):
    payment_type_description: DomainPaymentDescription
    bank_account_type_description: DomainBankAccountDescription


class ContactInformation(BaseModel):
    communication_type: DomainCommunication = Field(alias="communication_type_id")
    description: str
    contact: str
    observation: Optional[str] = None
    is_primary: bool


class ContactInformationRequest(ContactInformation, PersonIDMixin):
    pass


class ContactInformationResponse(ContactInformation, IDMixin, PersonIDMixin, TimeStampMixin):
    communication_type_description: DomainCommunicationDescription


class Document(BaseModel):
    document_type_id: DomainDocument = Field(alias="document_type")
    document_number: str
    issuing_agency: str
    issuing_date: datetime
    expiration_date: Optional[datetime] = None


class DocumentRequest(Document, PersonIDMixin):
    pass


class DocumentResponse(Document, IDMixin, PersonIDMixin, TimeStampMixin):
    document_type_description: DomainDocumentDescription


class AssignRoleRequest(BaseModel):
    role_id: int
    attributes: Optional[dict[str, Any]] = None


class AssignRoleResponse(IDMixin):
    name: str
    attributes: Optional[dict[str, Any]] = None


class ListPartyRolesResponse(PersonIDMixin):
    name: str
    roles: list[AssignRoleResponse]


class Party(BaseModel):
    person_type: DomainPerson = Field(alias="person_type_id")
    full_name: str
    preferred_name: Optional[str] = None
    company_name: Optional[str] = None
    document_number: Optional[str] = None
    birth_date: Optional[date] = None
    gender_type: DomainGender = Field(alias="gender_type_id")
    occupation: Optional[str] = None
    monthly_income: Optional[float] = None
    politically_exposed: Optional[bool] = None
    economic_activity: Optional[str] = None
    annual_gross_income: Optional[float] = None
    net_worth: Optional[float] = None
    addresses: list[Address] = Field(default_factory=list)
    contact_information: list[ContactInformation] = Field(default_factory=list, alias="communications")
    banking_details: list[BankingDetails] = Field(default_factory=list, alias="bank_accounts")
    documents: list[Document] = Field(default_factory=list)
    roles: list[AssignRoleRequest] = Field(default_factory=list)


class PartyResponse(Party, IDMixin, TimeStampMixin):
    person_type_description: DomainPersonDescription
    gender_type_description: DomainGenderDescription


## SEARCH AND PAGINATION SCHEMAS


class PaginationLinks(BaseModel):
    first: Optional[str] = None
    last: Optional[str] = None
    prev: Optional[str] = None
    next: Optional[str] = None


class PaginationMetaLinks(BaseModel):
    url: str
    label: str
    active: bool


class PaginationMeta(BaseModel):
    current_page: int
    from_: int
    last_page: int
    links: Optional[list[PaginationMetaLinks]] = None


class PaginationResponse[T: BaseModel](BaseModel):
    data: list[T]
    links: PaginationLinks
    meta: PaginationMeta


class BaseSearchParams(BaseModel):
    page: Optional[int] = Field(default=1, ge=1, description="Page number for pagination.")
    per_page: Optional[int] = Field(default=10, ge=1, le=100, description="Number of items per page for pagination.")
    filter: Optional[list[str]] = Field(
        default=None,
        alias="with",
        description="List of related resources to include in the response. "
        "Options: 'addresses', 'communications', 'bank_accounts', 'documents', 'roles'.",
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
