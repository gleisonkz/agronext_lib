from agro_pdf_generator.base_model import BaseModel


class PageConfig(BaseModel):
    width: str = "1192px"
    height: str = "1755px"
    padding: str = "24px"
