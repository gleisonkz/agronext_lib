def build_quotation_coverage_restrictions() -> str:
    # Coverage restrictions information
    coverage_restrictions_information = [
        "Para fins da Cláusula 8.1 - alínea d das Condições Gerais do Seguro, ",
        "com exceção ao período de plantio definido na proposta, soberano e ",
        "independente de qualquer outra norma ou disposição, são consideradas ",
        "recomendações técnicas dos órgãos oficiais aquelas definidas pelo ",
        "Zoneamento Agrícola de Risco Climático (ZARC) publicado pelo Ministério ",
        "da Agricultura, Pecuária e Abastecimento (MAPA) para o ano vigente. ",
        "A condução da cultura segurada pelo proponente em desacordo, parcial ou ",
        "total, às demais estritas condições e/ou orientações emanadas pelo MAPA, ",
        "dentre outras de igual relevância, acarretará na ineficácia absoluta da ",
        "cobertura e no imediato cancelamento do contrato de seguro por não aquisição ",
        "do direito à garantia.",
    ]
    return "".join(coverage_restrictions_information)
