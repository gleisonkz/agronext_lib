def build_quotation_available_documents(docs: list[str]) -> str:
    available_documents_information = [
        "DOCUMENTOS DISPONÍVEIS PARA CONSULTA",
        "As Condições Gerais, Especiais e Adicionais deste Seguro estão disponíveis no site da Seguradora: https://essor.com.br/condicoes-gerais/",
        "Verifique o texto correspondente às seguintes coberturas:",
    ]
    return "\n".join(available_documents_information + docs)