from enum import IntEnum, StrEnum


class Roles(IntEnum):
    BROKER = 1  # Corretor
    CLIENT = 2  # Cliente
    BENEFICIARY = 3  # Beneficiário
    ADJUSTER = 4  # Vistoriador
    AGRONOMIST = 5  # Perito Agrônomo


class RoleDescription(StrEnum):
    BROKER = "Corretor"
    CLIENT = "Cliente"
    BENEFICIARY = "Beneficiário"
    ADJUSTER = "Vistoriador"
    AGRONOMIST = "Perito"


class DomainTypes(StrEnum):
    ADDRESS = "address-types"
    BANK_ACCOUNT = "bank-account-types"
    COMMUNICATION = "communication-types"
    GENDER = "gender-types"
    PAYMENT = "payment-types"
    PERSON = "person-types"
    STATE = "state-types"
    DOCUMENT = "document-types"


class DomainAddress(IntEnum):
    MAILING = 1  # Correspondência
    TAX = 2  # Tributos
    COMMERCIAL = 3  # Comercial
    RESIDENTIAL = 4  # Residencial
    BILLING = 5  # Cobrança
    PROPERTY_RISK = 6  # Endereço de Risco Patrimonial


class DomainBankAccount(IntEnum):
    INDIVIDUAL_CHECKING = 1  # Conta corrente individual
    INDIVIDUAL_SAVINGS = 2  # Conta poupança individual
    INDIVIDUAL_JUDICIAL = 3  # Conta depósito judicial / depósito em consignação individual
    JOINT_CHECKING = 4  # Conta corrente conjunta
    JOINT_SAVINGS = 5  # Conta poupança conjunta
    JOINT_JUDICIAL = 6  # Conta depósito judicial / depósito em consignação conjunta


class DomainCommunication(IntEnum):
    EMAIL = 1  # E-mail
    MOBILE = 2  # Celular
    LANDLINE = 3  # Telefone Fixo
    WHATSAPP = 4  # WhatsApp


class DomainGender(IntEnum):
    MALE = 1  # Masculino
    FEMALE = 2  # Feminino
    OTHER = 3  # Outro
    PREFER_NOT_TO_SAY = 4  # Prefiro não informar


class DomainPayment(IntEnum):
    CHECK = 1  # Cheque
    DOC = 2  # DOC
    TED = 3  # TED
    TRANSFER = 4  # Transferência
    DARF = 5  # DARF NORMAL
    BOLETO = 6  # Boleto
    BANK_FILE = 7  # Arquivo Bancário
    EXCHANGE_REMITTANCE = 8  # Remessa de Câmbio
    DIRECT_DEBIT = 9  # Débito Automático
    INTERNAL_TRANSFER = 10  # Transferência entre Contas
    IDENTIFIED_DEPOSIT = 11  # Depósito Identificado
    WITHDRAWAL = 12  # Saque
    PAYMENT_ORDER = 13  # Ordem de Pagamento
    INVOICE = 14  # Nota Fiscal
    FEE = 15  # Tarifa
    DEPOSIT = 16  # Depósito
    REAL_TIME = 17  # Real Time


class DomainPerson(IntEnum):
    NATURAL_PERSON = 1  # Pessoa Física
    LEGAL_ENTITY = 2  # Pessoa Jurídica


class DomainState(IntEnum):
    ACRE = 1  # Acre
    ALAGOAS = 2  # Alagoas
    AMAPA = 3  # Amapá
    AMAZONAS = 4  # Amazonas
    BAHIA = 5  # Bahia
    CEARA = 6  # Ceará
    FEDERAL_DISTRICT = 7  # Distrito Federal
    ESPIRITO_SANTO = 8  # Espírito Santo
    GOIAS = 9  # Goiás
    MARANHAO = 10  # Maranhão
    MATO_GROSSO = 11  # Mato Grosso
    MATO_GROSSO_DO_SUL = 12  # Mato Grosso do Sul
    MINAS_GERAIS = 13  # Minas Gerais
    PARA = 14  # Pará
    PARAIBA = 15  # Paraíba
    PARANA = 16  # Paraná
    PERNAMBUCO = 17  # Pernambuco
    PIAUI = 18  # Piauí
    RIO_DE_JANEIRO = 19  # Rio de Janeiro
    RIO_GRANDE_DO_NORTE = 20  # Rio Grande do Norte
    RIO_GRANDE_DO_SUL = 21  # Rio Grande do Sul
    RONDONIA = 22  # Rondônia
    RORAIMA = 23  # Roraima
    SANTA_CATARINA = 24  # Santa Catarina
    SAO_PAULO = 25  # São Paulo
    SERGIPE = 26  # Sergipe
    TOCANTINS = 27  # Tocantins


class DomainDocument(IntEnum):
    RG = 1  # RG
    CNH = 2  # CNH
    RNE = 3  # RNE
    CIN = 4  # CIN
    CREA = 5  # CREA
    CFTA = 6  # CFTA


## Description Enums


class DomainAddressDescription(StrEnum):
    MAILING = "Correspondência"
    TAX = "Tributos"
    COMMERCIAL = "Comercial"
    RESIDENTIAL = "Residencial"
    BILLING = "Cobrança"
    PROPERTY_RISK = "Endereço de Risco Patrimonial"


class DomainBankAccountDescription(StrEnum):
    INDIVIDUAL_CHECKING = "Conta corrente individual"
    INDIVIDUAL_SAVINGS = "Conta poupança individual"
    INDIVIDUAL_JUDICIAL = "Conta depósito judicial / depósito em consignação individual"
    JOINT_CHECKING = "Conta corrente conjunta"
    JOINT_SAVINGS = "Conta poupança conjunta"
    JOINT_JUDICIAL = "Conta depósito judicial / depósito em consignação conjunta"


class DomainCommunicationDescription(StrEnum):
    EMAIL = "E-mail"
    MOBILE = "Celular"
    LANDLINE = "Telefone Fixo"
    WHATSAPP = "WhatsApp"


class DomainGenderDescription(StrEnum):
    MALE = "Masculino"
    FEMALE = "Feminino"
    OTHER = "Outro"
    PREFER_NOT_TO_SAY = "Prefiro não informar"


class DomainPaymentDescription(StrEnum):
    CHECK = "Cheque"
    DOC = "DOC"
    TED = "TED"
    TRANSFER = "Transferência"
    DARF = "DARF NORMAL"
    BOLETO = "Boleto"
    BANK_FILE = "Arquivo Bancário"
    EXCHANGE_REMITTANCE = "Remessa de Câmbio"
    DIRECT_DEBIT = "Débito Automático"
    INTERNAL_TRANSFER = "Transferência entre Contas"
    IDENTIFIED_DEPOSIT = "Depósito Identificado"
    WITHDRAWAL = "Saque"
    PAYMENT_ORDER = "Ordem de Pagamento"
    INVOICE = "Nota Fiscal"
    FEE = "Tarifa"
    DEPOSIT = "Depósito"
    REAL_TIME = "Real Time"


class DomainPersonDescription(StrEnum):
    INDIVIDUAL = "Pessoa Física"
    LEGAL_ENTITY = "Pessoa Jurídica"


class DomainStateDescription(StrEnum):
    ACRE = "Acre"
    ALAGOAS = "Alagoas"
    AMAPA = "Amapá"
    AMAZONAS = "Amazonas"
    BAHIA = "Bahia"
    CEARA = "Ceará"
    FEDERAL_DISTRICT = "Distrito Federal"
    ESPIRITO_SANTO = "Espírito Santo"
    GOIAS = "Goiás"
    MARANHAO = "Maranhão"
    MATO_GROSSO = "Mato Grosso"
    MATO_GROSSO_DO_SUL = "Mato Grosso do Sul"
    MINAS_GERAIS = "Minas Gerais"
    PARA = "Pará"
    PARAIBA = "Paraíba"
    PARANA = "Paraná"
    PERNAMBUCO = "Pernambuco"
    PIAUI = "Piauí"
    RIO_DE_JANEIRO = "Rio de Janeiro"
    RIO_GRANDE_DO_NORTE = "Rio Grande do Norte"
    RIO_GRANDE_DO_SUL = "Rio Grande do Sul"
    RONDONIA = "Rondônia"
    RORAIMA = "Roraima"
    SANTA_CATARINA = "Santa Catarina"
    SAO_PAULO = "São Paulo"
    SERGIPE = "Sergipe"
    TOCANTINS = "Tocantins"


class DomainDocumentDescription(StrEnum):
    RG = "RG"
    CNH = "CNH"
    RNE = "RNE"
    CIN = "CIN"
    CREA = "CREA"
    CFTA = "CFTA"
