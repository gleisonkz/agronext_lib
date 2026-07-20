from ...builders.quotation_block_builder import QuotationBlockBuilder
from ...builders.simulation_block_builder import SimulationBlockBuilder
from ...builders.policy_builder import build_policy_pdf
from ...generator import PdfGenerator
from ...schemas import PDFData, PolicyDocumentData


def generate_quotation_pdf(data: PDFData) -> bytes:
    block_builder = QuotationBlockBuilder(data)
    blocks = block_builder.build_all()

    generator = PdfGenerator()
    pdf_bytes = generator.generate_pdf(blocks)
    return pdf_bytes


def generate_simulation_pdf(data: PDFData) -> bytes:
    block_builder = SimulationBlockBuilder(data)
    blocks = block_builder.build_all()

    generator = PdfGenerator()
    pdf_bytes = generator.generate_pdf(blocks)
    return pdf_bytes


def generate_policy_pdf(
    data: PolicyDocumentData,
    logo_path: str,
    *,
    header_image_path: str | None = None,
    footer_image_path: str | None = None,
    signature_image_path: str | None = None,
    font_path: str | None = None,
) -> bytes:
    return build_policy_pdf(
        data,
        logo_path,
        header_image_path=header_image_path,
        footer_image_path=footer_image_path,
        signature_image_path=signature_image_path,
        font_path=font_path,
    )
