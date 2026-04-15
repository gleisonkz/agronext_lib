def build_available_documents(docs: list) -> str:
    available_documents_information = [
        "DOCUMENTOS DISPONÍVEIS PARA CONSULTA",
        "As Condições Gerais, Especiais e Adicionais deste Seguro estão disponíveis no site da Seguradora: https://essor.com.br/condicoes-gerais/",
        "Verifique o texto correspondente às seguintes coberturas:",
    ]
    docs_str = [doc.name or str(doc.blob_id) for doc in docs]
    return "\n".join(available_documents_information + docs_str)
