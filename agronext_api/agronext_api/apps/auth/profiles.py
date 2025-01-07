from enum import StrEnum


class Role(StrEnum):
    TECHNICAL = "technical"
    ADMINISTRATIVE_CLAIM = "administrative_claim"
    FIELD_CLAIM = "field_claim"
    COMMERCIAL = "commercial"
    TECHNICAL_MANAGER_BROKERAGE = "technical_manager_brokerage"
    SUPERVISOR_BROKERAGE = "supervisor_brokerage"
    SALES_OPERATOR = "sales_operator"
    CLAIM_OPERATOR = "claim_operator"
    ASSISTANT_BROKERAGE = "assistant_brokerage"
    ADMINISTRATIVE_BROKERAGE = "administrative_brokerage"
    MANAGER_SURVEY = "manager_survey"
    SURVEYOR = "surveyor"
    FIELD_ASSISTANT_SURVEY = "field_assistant_survey"
    ADMINISTRATIVE_SURVEY = "administrative_survey"
    MANAGER_ADVISORY = "manager_advisory"
    SUPERVISOR_ADVISORY = "supervisor_advisory"
    ANALYST_ADVISORY = "analyst_advisory"
    OPERATOR_ADVISORY = "operator_advisory"
    ASSISTANT_ADVISORY = "assistant_advisory"
    ADMINISTRATIVE_ADVISORY = "administrative_advisory"
    PARTNER_TECHNICAL = "partner_technical"
    PARTNER_CLAIM = "partner_claim"
    PARTNER_REINSURANCE = "partner_reinsurance"
    ALL = "all"


class SystemFeature(StrEnum):
    GROUP_PROFILE_REGISTRATION = "group_profile_registration"  # Cadastro de grupos de perfil
    USER_PROFILE_REGISTRATION = "user_profile_registration"  # Cadastro de perfil de usuário
    INTERNAL_USER_REGISTRATION = "internal_user_registration"  # Cadastro de usuário interno
    BROKERAGE_COMPANY_REGISTRATION = "brokerage_company_registration"  # Cadastro de empresas de corretagem
    BROKER_USER_REGISTRATION = "broker_user_registration"  # Cadastro de usuários corretores
    ASSOCIATED_COMPANY_REGISTRATION = (
        "associated_company_registration"  # Cadastro de empresas associadas (associados aos corretores)
    )
    ADVISORY_COMPANY_REGISTRATION = "advisory_company_registration"  # Cadastro de empresas de assessoria
    ADVISORY_USER_REGISTRATION = "advisory_user_registration"  # Cadastro de usuários de assessorias
    INSPECTION_COMPANY_REGISTRATION = "inspection_company_registration"  # Cadastro de empresas de vistoria
    INSPECTION_USER_REGISTRATION = "inspection_user_registration"  # Cadastro de usuários de vistorias
    OTHER_COMPANY_REGISTRATION = "other_company_registration"  # Cadastro de outras empresas
    EXTERNAL_USER_REGISTRATION = "external_user_registration"  # Cadastro de usuários externos - outros usuários
    QUOTATIONS_AND_PROPOSALS = "quotations_and_proposals"  # Cotação e propostas
    ENDORSEMENTS = "endorsements"  # Endosso
    RENEWAL_CONTRACT = "renewal_contract"  # Contrato de renovação
    POLICY_MANAGEMENT = "policy_management"  # Gestão de apólices
    TICKETS = "tickets"  # Chamados
    TICKET_TYPE_REGISTRATION = "ticket_type_registration"  # Cadastro de tipos de chamados
    AUTHORITY_LEVEL_REGISTRATION = "authority_level_registration"  # Cadastro de níveis de autoridade (fase 3)
    CLAIMS_PROCESS_LISTING = "claims_process_listing"  # Listagem de processos de sinistros
    CLAIM_NOTIFICATIONS = "claim_notifications"  # Avisos de sinistro, início e final de colheita, final de replantio
    INDEMNITY_ESTIMATES = "indemnity_estimates"  # Estimativa de indenizações
    INDEMNITY_CALCULATION = "indemnity_calculation"  # Cálculo de indenizações
    INDEMNITY_PAYMENTS = "indemnity_payments"  # Pagamento de indenizações
    SERVICE_ORDER_QUERY = "service_order_query"  # Consulta de ordens de serviço
    ROUTE_MANAGEMENT = "route_management"  # Gestão das rotas
    EXPENSE_LAUNCH = "expense_launch"  # Lançamento de despesas
    SCHEDULING = "scheduling"  # Agendamentos
    FEE_PAYMENT = "fee_payment"  # Pagamento de honorários
    DEBTOR_QUERY = "debtor_query"  # Consulta inadimplentes (Financeiro)
    PRODUCT_REGISTRATION = "product_registration"  # Cadastro de produtos
    COVERAGE_REGISTRATION = "coverage_registration"  # Cadastro de coberturas
    CULTURE_REGISTRATION = "culture_registration"  # Cadastro de culturas
    VARIETY_REGISTRATION = "variety_registration"  # Cadastro de variedades
    PAYMENT_CONDITIONS = "payment_conditions"  # Condições de pagamento
    QUESTIONNAIRE = "questionnaire"  # Questionário
    CYCLE_REGISTRATION = "cycle_registration"  # Cadastro de ciclos
    BRANCH_REGISTRATION = "branch_registration"  # Cadastro de ramos
    CULTIVATION_TYPE_REGISTRATION = "cultivation_type_registration"  # Cadastro de tipos de cultivo
    PHENOLOGICAL_STAGE_GROUP_REGISTRATION = (
        "phenological_stage_group_registration"  # Cadastro de grupos de estádio fenológico
    )
    RISK_TYPE_REGISTRATION = "risk_type_registration"  # Cadastro de tipos de risco
    SUSEP_CODE_REGISTRATION = "susep_code_registration"  # Cadastro de código SUSEP
    UNIT_OF_MEASURE_REGISTRATION = "unit_of_measure_registration"  # Cadastro de unidades de medida
    HARVEST_REGISTRATION = "harvest_registration"  # Cadastro de safras
    SOIL_TYPE_REGISTRATION = "soil_type_registration"  # Cadastro de tipos de solo
    GENERAL_CONDITIONS_REGISTRATION = "general_conditions_registration"  # Cadastro de condições gerais
    COMPLEMENTARY_CONDITIONS_REGISTRATION = (
        "complementary_conditions_registration"  # Cadastro de condições complementares
    )
    PARTICULAR_CONDITIONS_REGISTRATION = "particular_conditions_registration"  # Cadastro de condições particulares
    SPECIAL_CONDITIONS_REGISTRATION = "special_conditions_registration"  # Cadastro de condições especiais
    REGION_REGISTRATION = "region_registration"  # Cadastro de regiões
    RATE_REGISTRATION = "rate_registration"  # Cadastro de taxas
    ADDITIONAL_COMMISSION_REGISTRATION = (
        "additional_commission_registration"  # Cadastro de comissão adicional Agrobrasil
    )
    STANDARD_COMMISSION_REGISTRATION = "standard_commission_registration"  # Cadastro padrão de comissões
    REINSURANCE_CONTRACT_REGISTRATION = "reinsurance_contract_registration"  # Cadastro de contrato de resseguro
    POCKET_REGISTRATION = "pocket_registration"  # Cadastro de pockets
    CAPACITY_MAINTENANCE = "capacity_maintenance"  # Cadastro e manutenção de capacidades
    MUNICIPALITY_CAPACITY_REGISTRATION = "municipality_capacity_registration"  # Cadastro de capacidades para municípios
    BENEFICIARY_REGISTRATION = "beneficiary_registration"  # Cadastro de beneficiários
    INSURED_REGISTRATION = "insured_registration"  # Cadastro de segurados
    NOTIFICATION_CENTER = "notification_center"


resource_permissions = {
    SystemFeature.GROUP_PROFILE_REGISTRATION: {
        "required_roles": [Role.TECHNICAL, Role.ADMINISTRATIVE_CLAIM],
        "additional_rule": [],
    },
    SystemFeature.USER_PROFILE_REGISTRATION: {
        "required_roles": [Role.TECHNICAL, Role.ADMINISTRATIVE_CLAIM],
        "additional_rule": [],
    },
    SystemFeature.INTERNAL_USER_REGISTRATION: {
        "required_roles": [],
        "additional_rule": [
            {
                "roles": [
                    Role.TECHNICAL,
                    Role.ADMINISTRATIVE_CLAIM,
                    Role.FIELD_CLAIM,
                    Role.COMMERCIAL,
                    Role.TECHNICAL_MANAGER_BROKERAGE,
                    Role.SUPERVISOR_BROKERAGE,
                    Role.MANAGER_SURVEY,
                    Role.SURVEYOR,
                    Role.MANAGER_ADVISORY,
                    Role.SUPERVISOR_ADVISORY,
                ],
                "methods": ["GET"],
            }
        ],
    },
    SystemFeature.BROKERAGE_COMPANY_REGISTRATION: {
        "required_roles": [
            Role.TECHNICAL,
            Role.ADMINISTRATIVE_ADVISORY,
            Role.SUPERVISOR_ADVISORY,
            Role.ANALYST_ADVISORY,
        ],
        "additional_rule": [
            {
                "roles": [Role.ADMINISTRATIVE_CLAIM, Role.FIELD_CLAIM, Role.COMMERCIAL],
                "methods": ["GET"],
            },
            {
                "roles": [Role.TECHNICAL_MANAGER_BROKERAGE, Role.SUPERVISOR_BROKERAGE],
                "methods": ["GET, PUT, PATH"],
            },
        ],
    },
    SystemFeature.BROKER_USER_REGISTRATION: {
        "required_roles": [
            Role.TECHNICAL,
            Role.TECHNICAL_MANAGER_BROKERAGE,
            Role.SUPERVISOR_BROKERAGE,
        ],
        "additional_rule": [
            {
                "roles": [
                    Role.ADMINISTRATIVE_CLAIM,
                    Role.COMMERCIAL,
                    Role.SALES_OPERATOR,
                    Role.CLAIM_OPERATOR,
                    Role.ASSISTANT_BROKERAGE,
                    Role.ADMINISTRATIVE_BROKERAGE,
                    Role.ADMINISTRATIVE_ADVISORY,
                    Role.SUPERVISOR_ADVISORY,
                    Role.ANALYST_ADVISORY,
                ],
                "methods": ["GET"],
            },
        ],
    },
    SystemFeature.ASSOCIATED_COMPANY_REGISTRATION: {
        "required_roles": [
            Role.TECHNICAL,
            Role.TECHNICAL_MANAGER_BROKERAGE,
            Role.SUPERVISOR_BROKERAGE,
        ],
        "additional_rule": [
            {
                "roles": [
                    Role.ADMINISTRATIVE_CLAIM,
                    Role.FIELD_CLAIM,
                    Role.COMMERCIAL,
                    Role.MANAGER_ADVISORY,
                    Role.SUPERVISOR_ADVISORY,
                    Role.ANALYST_ADVISORY,
                ],
                "methods": ["GET"],
            }
        ],
    },
    SystemFeature.ADVISORY_COMPANY_REGISTRATION: {
        "required_roles": [
            Role.TECHNICAL,
            Role.ADMINISTRATIVE_ADVISORY,
            Role.MANAGER_ADVISORY,
            Role.SUPERVISOR_ADVISORY,
        ],
        "additional_rule": [
            {
                "roles": [Role.ADMINISTRATIVE_CLAIM, Role.FIELD_CLAIM, Role.COMMERCIAL],
                "methods": ["GET"],
            },
            {
                "roles": [Role.TECHNICAL_MANAGER_BROKERAGE, Role.SUPERVISOR_BROKERAGE],
                "methods": ["GET", "PUT", "PATCH"],
            },
        ],
    },
    SystemFeature.ADVISORY_USER_REGISTRATION: {
        "required_roles": [
            Role.TECHNICAL,
            Role.ADMINISTRATIVE_ADVISORY,
            Role.MANAGER_ADVISORY,
            Role.SUPERVISOR_ADVISORY,
        ],
        "additional_rule": [
            {
                "roles": [
                    Role.ADMINISTRATIVE_CLAIM,
                    Role.COMMERCIAL,
                    Role.ANALYST_ADVISORY,
                    Role.OPERATOR_ADVISORY,
                    Role.ASSISTANT_ADVISORY,
                    Role.ADMINISTRATIVE_ADVISORY,
                ],
                "methods": ["GET"],
            }
        ],
    },
    SystemFeature.INSPECTION_COMPANY_REGISTRATION: {
        "required_roles": [Role.ADMINISTRATIVE_CLAIM, Role.ADMINISTRATIVE_SURVEY],
        "additional_rule": [
            {
                "roles": [Role.TECHNICAL, Role.FIELD_CLAIM, Role.COMMERCIAL],
                "methods": ["GET"],
            },
            {
                "roles": [Role.ADMINISTRATIVE_SURVEY, Role.MANAGER_SURVEY],
                "methods": ["GET", "PATCH", "PUT"],
            },
        ],
    },
    SystemFeature.INSPECTION_USER_REGISTRATION: {
        "required_roles": [Role.ADMINISTRATIVE_CLAIM, Role.MANAGER_SURVEY],
        "additional_rule": [
            {
                "roles": [
                    Role.TECHNICAL,
                    Role.COMMERCIAL,
                    Role.SURVEYOR,
                    Role.FIELD_ASSISTANT_SURVEY,
                    Role.ADMINISTRATIVE_SURVEY,
                ],
                "methods": ["GET"],
            },
            {"roles": [Role.FIELD_CLAIM], "methods": ["GET", "PATCH", "PUT"]},
        ],
    },
    SystemFeature.OTHER_COMPANY_REGISTRATION: {
        "required_roles": [Role.TECHNICAL],
        "additional_rule": [
            {
                "roles": [Role.ADMINISTRATIVE_CLAIM, Role.FIELD_CLAIM],
                "methods": ["GET"],
            },
            {
                "roles": [Role.PARTNER_TECHNICAL, Role.PARTNER_CLAIM, Role.COMMERCIAL],
                "methods": ["GET", "PUT", "PATCH"],
            },
        ],
    },
    SystemFeature.EXTERNAL_USER_REGISTRATION: {
        "required_roles": [Role.TECHNICAL, Role.PARTNER_TECHNICAL, Role.PARTNER_CLAIM],
        "additional_rule": [
            {
                "roles": [Role.ADMINISTRATIVE_CLAIM, Role.FIELD_CLAIM, Role.COMMERCIAL],
                "methods": ["GET"],
            }
        ],
    },
    SystemFeature.QUOTATIONS_AND_PROPOSALS: {
        "required_roles": [
            Role.TECHNICAL,
            Role.ADMINISTRATIVE_CLAIM,
            Role.FIELD_CLAIM,
            Role.COMMERCIAL,
            Role.TECHNICAL_MANAGER_BROKERAGE,
            Role.SUPERVISOR_BROKERAGE,
            Role.SALES_OPERATOR,
        ],
        "additional_rule": [
            {
                "roles": [
                    Role.MANAGER_ADVISORY,
                    Role.SUPERVISOR_ADVISORY,
                    Role.ANALYST_ADVISORY,
                    Role.OPERATOR_ADVISORY,
                    Role.ASSISTANT_ADVISORY,
                    Role.PARTNER_TECHNICAL,
                ],
                "methods": ["GET"],
            }
        ],
    },
    SystemFeature.ENDORSEMENTS: {
        "required_roles": [
            Role.TECHNICAL,
            Role.ADMINISTRATIVE_CLAIM,
            Role.FIELD_CLAIM,
            Role.COMMERCIAL,
            Role.TECHNICAL_MANAGER_BROKERAGE,
            Role.SUPERVISOR_BROKERAGE,
            Role.SALES_OPERATOR,
        ],
        "additional_rule": [
            {
                "roles": [
                    Role.MANAGER_ADVISORY,
                    Role.SUPERVISOR_ADVISORY,
                    Role.ANALYST_ADVISORY,
                    Role.OPERATOR_ADVISORY,
                    Role.ASSISTANT_ADVISORY,
                ],
                "methods": ["GET"],
            },
        ],
    },
    SystemFeature.RENEWAL_CONTRACT: {
        "required_roles": [
            Role.TECHNICAL,
            Role.ADMINISTRATIVE_CLAIM,
            Role.FIELD_CLAIM,
            Role.COMMERCIAL,
            Role.TECHNICAL_MANAGER_BROKERAGE,
            Role.SUPERVISOR_BROKERAGE,
            Role.SALES_OPERATOR,
        ],
        "additional_rule": [
            {
                "roles": [
                    Role.MANAGER_ADVISORY,
                    Role.SUPERVISOR_ADVISORY,
                    Role.ANALYST_ADVISORY,
                    Role.OPERATOR_ADVISORY,
                    Role.ASSISTANT_ADVISORY,
                ],
                "methods": ["GET"],
            },
        ],
    },
    SystemFeature.POLICY_MANAGEMENT: {
        "required_roles": [Role.TECHNICAL],
        "additional_rule": [],
    },
    SystemFeature.TICKETS: {
        "required_roles": [
            Role.TECHNICAL,
            Role.ADMINISTRATIVE_CLAIM,
            Role.FIELD_CLAIM,
            Role.COMMERCIAL,
        ],
        "additional_rule": [{"roles": [Role.ALL], "methods": ["POST", "GET"]}],
    },
    SystemFeature.TICKET_TYPE_REGISTRATION: {
        "required_roles": [Role.TECHNICAL, Role.ADMINISTRATIVE_CLAIM],
        "additional_rule": [{"roles": [Role.COMMERCIAL, Role.FIELD_CLAIM], "methods": ["GET"]}],
    },
    SystemFeature.AUTHORITY_LEVEL_REGISTRATION: {
        "required_roles": [Role.TECHNICAL, Role.ADMINISTRATIVE_CLAIM],
        "additional_rule": [],
    },
    SystemFeature.CLAIMS_PROCESS_LISTING: {
        "required_roles": [Role.ADMINISTRATIVE_CLAIM],
        "additional_rule": [
            {
                "roles": [
                    Role.TECHNICAL,
                    Role.COMMERCIAL,
                    Role.FIELD_CLAIM,
                    Role.TECHNICAL_MANAGER_BROKERAGE,
                    Role.ADMINISTRATIVE_BROKERAGE,
                ],
                "methods": ["GET"],
            }
        ],
    },
    SystemFeature.CLAIM_NOTIFICATIONS: {
        "required_roles": [
            Role.ADMINISTRATIVE_CLAIM,
            Role.FIELD_CLAIM,
            Role.MANAGER_SURVEY,
            Role.ADMINISTRATIVE_SURVEY,
            Role.SURVEYOR,
        ],
        "additional_rule": [
            {
                "roles": [
                    Role.TECHNICAL,
                    Role.FIELD_CLAIM,
                    Role.COMMERCIAL,
                    Role.TECHNICAL_MANAGER_BROKERAGE,
                    Role.SUPERVISOR_BROKERAGE,
                    Role.CLAIM_OPERATOR,
                    Role.FIELD_ASSISTANT_SURVEY,
                    Role.MANAGER_ADVISORY,
                    Role.SUPERVISOR_ADVISORY,
                    Role.OPERATOR_ADVISORY,
                    Role.PARTNER_CLAIM,
                ],
                "methods": ["GET"],
            }
        ],
    },
    SystemFeature.INDEMNITY_ESTIMATES: {
        "required_roles": [Role.ADMINISTRATIVE_CLAIM],
        "additional_rule": [
            {
                "roles": [Role.TECHNICAL, Role.FIELD_CLAIM, Role.COMMERCIAL],
                "methods": ["GET"],
            }
        ],
    },
    SystemFeature.INDEMNITY_CALCULATION: {
        "required_roles": [Role.ADMINISTRATIVE_CLAIM],
        "additional_rule": [
            {
                "roles": [
                    Role.TECHNICAL,
                    Role.FIELD_CLAIM,
                    Role.COMMERCIAL,
                    Role.TECHNICAL_MANAGER_BROKERAGE,
                    Role.SUPERVISOR_BROKERAGE,
                    Role.CLAIM_OPERATOR,
                    Role.ADMINISTRATIVE_BROKERAGE,
                ],
                "methods": ["GET"],
            }
        ],
    },
    SystemFeature.INDEMNITY_PAYMENTS: {
        "required_roles": [Role.ADMINISTRATIVE_CLAIM],
        "additional_rule": [
            {
                "roles": [
                    Role.TECHNICAL,
                    Role.FIELD_CLAIM,
                    Role.COMMERCIAL,
                    Role.TECHNICAL_MANAGER_BROKERAGE,
                    Role.SUPERVISOR_BROKERAGE,
                    Role.CLAIM_OPERATOR,
                    Role.ADMINISTRATIVE_BROKERAGE,
                    Role.MANAGER_SURVEY,
                    Role.SURVEYOR,
                    Role.ADMINISTRATIVE_SURVEY,
                ],
                "methods": ["GET"],
            }
        ],
    },
    SystemFeature.SERVICE_ORDER_QUERY: {
        "required_roles": [
            Role.ADMINISTRATIVE_CLAIM,
            Role.FIELD_CLAIM,
            Role.MANAGER_SURVEY,
            Role.SURVEYOR,
            Role.ADMINISTRATIVE_SURVEY,
        ],
        "additional_rule": [
            {
                "roles": [
                    Role.TECHNICAL,
                    Role.COMMERCIAL,
                ],
                "methods": ["GET"],
            }
        ],
    },
    SystemFeature.ROUTE_MANAGEMENT: {
        "required_roles": [Role.ADMINISTRATIVE_CLAIM, Role.FIELD_CLAIM],
        "additional_rule": [
            {
                "roles": [
                    Role.TECHNICAL,
                    Role.COMMERCIAL,
                    Role.MANAGER_SURVEY,
                    Role.SURVEYOR,
                    Role.FIELD_ASSISTANT_SURVEY,
                    Role.ADMINISTRATIVE_SURVEY,
                ],
                "methods": ["GET"],
            }
        ],
    },
    SystemFeature.EXPENSE_LAUNCH: {
        "required_roles": [
            Role.ADMINISTRATIVE_CLAIM,
            Role.MANAGER_SURVEY,
            Role.SURVEYOR,
            Role.ADMINISTRATIVE_SURVEY,
        ],
        "additional_rule": [
            {
                "roles": [
                    Role.FIELD_CLAIM,
                    Role.FIELD_ASSISTANT_SURVEY,
                ],
                "methods": ["GET"],
            }
        ],
    },
    SystemFeature.SCHEDULING: {
        "required_roles": [
            Role.ADMINISTRATIVE_CLAIM,
            Role.FIELD_CLAIM,
            Role.MANAGER_SURVEY,
            Role.SURVEYOR,
            Role.ADMINISTRATIVE_SURVEY,
            Role.MANAGER_ADVISORY,
            Role.SURVEYOR,
            Role.ADMINISTRATIVE_SURVEY,
        ],
        "additional_rule": [
            {
                "roles": [
                    Role.TECHNICAL,
                    Role.COMMERCIAL,
                    Role.TECHNICAL_MANAGER_BROKERAGE,
                    Role.SUPERVISOR_BROKERAGE,
                    Role.CLAIM_OPERATOR,
                    Role.ADMINISTRATIVE_BROKERAGE,
                    Role.FIELD_ASSISTANT_SURVEY,
                ],
                "methods": ["GET"],
            }
        ],
    },
    SystemFeature.FEE_PAYMENT: {
        "required_roles": [
            Role.ADMINISTRATIVE_CLAIM,
            Role.MANAGER_SURVEY,
            Role.SURVEYOR,
            Role.ADMINISTRATIVE_SURVEY,
            Role.MANAGER_ADVISORY,
            Role.SURVEYOR,
            Role.ADMINISTRATIVE_SURVEY,
        ],
        "additional_rule": [
            {
                "roles": [Role.FIELD_CLAIM, Role.FIELD_ASSISTANT_SURVEY],
                "methods": ["GET"],
            }
        ],
    },
    SystemFeature.DEBTOR_QUERY: {
        "required_roles": [
            Role.TECHNICAL,
            Role.COMMERCIAL,
            Role.TECHNICAL_MANAGER_BROKERAGE,
            Role.SUPERVISOR_BROKERAGE,
            Role.SALES_OPERATOR,
        ],
        "additional_rule": [
            {
                "roles": [
                    Role.ADMINISTRATIVE_CLAIM,
                    Role.FIELD_CLAIM,
                    Role.MANAGER_ADVISORY,
                    Role.SUPERVISOR_ADVISORY,
                    Role.OPERATOR_ADVISORY,
                ],
                "methods": ["GET"],
            }
        ],
    },
    SystemFeature.PRODUCT_REGISTRATION: {
        "required_roles": [
            Role.TECHNICAL,
        ],
        "additional_rule": [
            {
                "roles": [
                    Role.ADMINISTRATIVE_CLAIM,
                ],
                "methods": ["GET"],
            }
        ],
    },
    SystemFeature.COVERAGE_REGISTRATION: {
        "required_roles": [
            Role.TECHNICAL,
        ],
        "additional_rule": [
            {
                "roles": [
                    Role.ADMINISTRATIVE_CLAIM,
                ],
                "methods": ["GET"],
            }
        ],
    },
    SystemFeature.CULTURE_REGISTRATION: {
        "required_roles": [
            Role.TECHNICAL,
        ],
        "additional_rule": [
            {
                "roles": [
                    Role.ADMINISTRATIVE_CLAIM,
                ],
                "methods": ["GET"],
            }
        ],
    },
    SystemFeature.VARIETY_REGISTRATION: {
        "required_roles": [
            Role.TECHNICAL,
        ],
        "additional_rule": [
            {
                "roles": [
                    Role.ADMINISTRATIVE_CLAIM,
                ],
                "methods": ["GET"],
            }
        ],
    },
    SystemFeature.PAYMENT_CONDITIONS: {
        "required_roles": [
            Role.TECHNICAL,
        ],
        "additional_rule": [
            {
                "roles": [
                    Role.ADMINISTRATIVE_CLAIM,
                ],
                "methods": ["GET"],
            }
        ],
    },
    SystemFeature.QUESTIONNAIRE: {
        "required_roles": [
            Role.TECHNICAL,
        ],
        "additional_rule": [
            {
                "roles": [
                    Role.ADMINISTRATIVE_CLAIM,
                ],
                "methods": ["GET"],
            }
        ],
    },
    SystemFeature.CYCLE_REGISTRATION: {
        "required_roles": [
            Role.TECHNICAL,
        ],
        "additional_rule": [
            {
                "roles": [
                    Role.ADMINISTRATIVE_CLAIM,
                ],
                "methods": ["GET"],
            }
        ],
    },
    SystemFeature.BRANCH_REGISTRATION: {
        "required_roles": [
            Role.TECHNICAL,
        ],
        "additional_rule": [
            {
                "roles": [
                    Role.ADMINISTRATIVE_CLAIM,
                ],
                "methods": ["GET"],
            }
        ],
    },
    SystemFeature.CULTIVATION_TYPE_REGISTRATION: {
        "required_roles": [
            Role.TECHNICAL,
        ],
        "additional_rule": [
            {
                "roles": [
                    Role.ADMINISTRATIVE_CLAIM,
                ],
                "methods": ["GET"],
            }
        ],
    },
    SystemFeature.PHENOLOGICAL_STAGE_GROUP_REGISTRATION: {
        "required_roles": [
            Role.TECHNICAL,
        ],
        "additional_rule": [
            {
                "roles": [
                    Role.ADMINISTRATIVE_CLAIM,
                ],
                "methods": ["GET"],
            }
        ],
    },
    SystemFeature.RISK_TYPE_REGISTRATION: {
        "required_roles": [
            Role.TECHNICAL,
        ],
        "additional_rule": [
            {
                "roles": [
                    Role.ADMINISTRATIVE_CLAIM,
                ],
                "methods": ["GET"],
            }
        ],
    },
    SystemFeature.SUSEP_CODE_REGISTRATION: {
        "required_roles": [
            Role.TECHNICAL,
        ],
        "additional_rule": [
            {
                "roles": [
                    Role.ADMINISTRATIVE_CLAIM,
                ],
                "methods": ["GET"],
            }
        ],
    },
    SystemFeature.UNIT_OF_MEASURE_REGISTRATION: {
        "required_roles": [
            Role.TECHNICAL,
        ],
        "additional_rule": [
            {
                "roles": [
                    Role.ADMINISTRATIVE_CLAIM,
                ],
                "methods": ["GET"],
            }
        ],
    },
    SystemFeature.HARVEST_REGISTRATION: {
        "required_roles": [
            Role.TECHNICAL,
        ],
        "additional_rule": [
            {
                "roles": [
                    Role.ADMINISTRATIVE_CLAIM,
                ],
                "methods": ["GET"],
            }
        ],
    },
    SystemFeature.SOIL_TYPE_REGISTRATION: {
        "required_roles": [
            Role.TECHNICAL,
        ],
        "additional_rule": [
            {
                "roles": [
                    Role.ADMINISTRATIVE_CLAIM,
                ],
                "methods": ["GET"],
            }
        ],
    },
    SystemFeature.GENERAL_CONDITIONS_REGISTRATION: {
        "required_roles": [
            Role.TECHNICAL,
        ],
        "additional_rule": [
            {
                "roles": [
                    Role.ADMINISTRATIVE_CLAIM,
                ],
                "methods": ["GET"],
            }
        ],
    },
    SystemFeature.COMPLEMENTARY_CONDITIONS_REGISTRATION: {
        "required_roles": [
            Role.TECHNICAL,
        ],
        "additional_rule": [
            {
                "roles": [
                    Role.ADMINISTRATIVE_CLAIM,
                ],
                "methods": ["GET"],
            }
        ],
    },
    SystemFeature.PARTICULAR_CONDITIONS_REGISTRATION: {
        "required_roles": [
            Role.TECHNICAL,
        ],
        "additional_rule": [
            {
                "roles": [
                    Role.ADMINISTRATIVE_CLAIM,
                ],
                "methods": ["GET"],
            }
        ],
    },
    SystemFeature.SPECIAL_CONDITIONS_REGISTRATION: {
        "required_roles": [
            Role.TECHNICAL,
        ],
        "additional_rule": [
            {
                "roles": [
                    Role.ADMINISTRATIVE_CLAIM,
                ],
                "methods": ["GET"],
            }
        ],
    },
    SystemFeature.REGION_REGISTRATION: {
        "required_roles": [
            Role.TECHNICAL,
        ],
        "additional_rule": [
            {
                "roles": [
                    Role.ADMINISTRATIVE_CLAIM,
                ],
                "methods": ["GET"],
            }
        ],
    },
    SystemFeature.RATE_REGISTRATION: {
        "required_roles": [
            Role.TECHNICAL,
        ],
        "additional_rule": [
            {
                "roles": [
                    Role.ADMINISTRATIVE_CLAIM,
                ],
                "methods": ["GET"],
            }
        ],
    },
    SystemFeature.ADDITIONAL_COMMISSION_REGISTRATION: {
        "required_roles": [
            Role.TECHNICAL,
        ],
        "additional_rule": [
            {
                "roles": [
                    Role.ADMINISTRATIVE_CLAIM,
                ],
                "methods": ["GET"],
            }
        ],
    },
    SystemFeature.STANDARD_COMMISSION_REGISTRATION: {
        "required_roles": [
            Role.TECHNICAL,
        ],
        "additional_rule": [
            {
                "roles": [
                    Role.ADMINISTRATIVE_CLAIM,
                ],
                "methods": ["GET"],
            }
        ],
    },
    SystemFeature.REINSURANCE_CONTRACT_REGISTRATION: {
        "required_roles": [
            Role.TECHNICAL,
        ],
        "additional_rule": [{"roles": [Role.ADMINISTRATIVE_CLAIM, Role.COMMERCIAL], "methods": ["GET"]}],
    },
    SystemFeature.POCKET_REGISTRATION: {
        "required_roles": [
            Role.TECHNICAL,
        ],
        "additional_rule": [{"roles": [Role.ADMINISTRATIVE_CLAIM, Role.COMMERCIAL], "methods": ["GET"]}],
    },
    SystemFeature.CAPACITY_MAINTENANCE: {
        "required_roles": [
            Role.TECHNICAL,
        ],
        "additional_rule": [{"roles": [Role.ADMINISTRATIVE_CLAIM, Role.COMMERCIAL], "methods": ["GET"]}],
    },
    SystemFeature.MUNICIPALITY_CAPACITY_REGISTRATION: {
        "required_roles": [
            Role.TECHNICAL,
        ],
        "additional_rule": [{"roles": [Role.ADMINISTRATIVE_CLAIM, Role.COMMERCIAL], "methods": ["GET"]}],
    },
    SystemFeature.BENEFICIARY_REGISTRATION: {
        "required_roles": [Role.TECHNICAL, Role.ADMINISTRATIVE_CLAIM],
        "additional_rule": [
            {
                "roles": [
                    Role.ADMINISTRATIVE_CLAIM,
                    Role.COMMERCIAL,
                    Role.TECHNICAL_MANAGER_BROKERAGE,
                    Role.ADMINISTRATIVE_BROKERAGE,
                    Role.SUPERVISOR_BROKERAGE,
                    Role.SALES_OPERATOR,
                    Role.CLAIM_OPERATOR,
                ],
                "methods": ["GET", "POST"],
            }
        ],
    },
    SystemFeature.INSURED_REGISTRATION: {
        "required_roles": [Role.TECHNICAL, Role.ADMINISTRATIVE_CLAIM],
        "additional_rule": [
            {
                "roles": [
                    Role.ADMINISTRATIVE_CLAIM,
                    Role.COMMERCIAL,
                    Role.TECHNICAL_MANAGER_BROKERAGE,
                    Role.ADMINISTRATIVE_BROKERAGE,
                    Role.SUPERVISOR_BROKERAGE,
                    Role.SALES_OPERATOR,
                    Role.CLAIM_OPERATOR,
                ],
                "methods": ["GET", "POST"],
            }
        ],
    },
    SystemFeature.NOTIFICATION_CENTER: {
        "required_roles": [Role.TECHNICAL, Role.ADMINISTRATIVE_CLAIM],
        "additional_rule": [],
    },
}
