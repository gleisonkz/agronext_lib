from ...builders.quotation_block_builder import QuotationBlockBuilder
from ...builders.simulation_block_builder import SimulationBlockBuilder
from ...generator import PdfGenerator
from ...schemas import PDFData


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
