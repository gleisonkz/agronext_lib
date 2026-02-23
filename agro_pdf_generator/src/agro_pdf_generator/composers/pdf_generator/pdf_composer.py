from ...builders.quotation_block_builder import QuotationBlockBuilder
from ...generator import PdfGenerator
from ...schemas import PDFData


def generate_quotation_pdf(data: PDFData) -> bytes:
    block_builder = QuotationBlockBuilder(data)
    blocks = block_builder.build_all()

    generator = PdfGenerator()
    pdf_bytes = generator.generate_pdf(blocks)
    return pdf_bytes
