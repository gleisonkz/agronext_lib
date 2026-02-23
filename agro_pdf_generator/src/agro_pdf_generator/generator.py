from pathlib import Path

from weasyprint import HTML

from agro_pdf_generator.blocks import BlockConfig, render_blocks_to_pages
from agro_pdf_generator.layout import build_full_page, get_base_css


class PdfGenerator:
    def __init__(self, base_url: str | None = None) -> None:
        self._base_url = base_url or str(Path(__file__).parent)

    def generate_pdf(self, blocks: list[BlockConfig]) -> bytes:
        html = self.generate_html(blocks)
        return self._convert_to_pdf(html)

    def generate_html(self, blocks: list[BlockConfig]) -> str:
        pages = render_blocks_to_pages(blocks)
        return self._build_document(pages)

    def generate_to_file(
        self,
        blocks: list[BlockConfig],
        output_path: Path | str,
    ) -> Path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        pdf_bytes = self.generate_pdf(blocks)
        output_path.write_bytes(pdf_bytes)
        return output_path

    def _build_document(self, pages: list[str]) -> str:
        total = len(pages)
        full_pages = []

        for i, content in enumerate(pages):
            page_content = content.replace("{{page}}", f"{i + 1} de {total}")
            full_pages.append(build_full_page(page_content))

        css = get_base_css()

        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Documento PDF</title>
    <style>{css}</style>
</head>
<body>{chr(10).join(full_pages)}</body>
</html>"""

    def _convert_to_pdf(self, html: str) -> bytes:
        return HTML(string=html, base_url=self._base_url).write_pdf()
