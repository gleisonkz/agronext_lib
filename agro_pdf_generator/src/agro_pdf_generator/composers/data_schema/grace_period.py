def build_grace_period() -> str:
    # Grace period information
    grace_period_information = [
        "CARÊNCIA DA COBERTURA PRINCIPAL:",
        "1 - O período de carência para esta cobertura será de 2 (dois) dias completos, contados a partir do início de vigência do seguro.",
        "1.1 - Caso 70% (setenta por cento) dos frutos não tiverem atingido um diâmetro superior a 3 (três) milímetros, o período de carência será prorrogado até que se cumpra esta condição.",
    ]
    return "\n".join(grace_period_information)
