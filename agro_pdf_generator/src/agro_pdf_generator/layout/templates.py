from functools import lru_cache

from agro_pdf_generator.config import Spacing, Layout, Styles


def build_logo_header(logo_path: str) -> str:
    return f'''
        <div style="text-align: center; height: {Layout.LOGO_HEADER_HEIGHT};
                    padding-top: {Layout.LOGO_HEADER_PADDING}; padding-bottom: {Layout.LOGO_HEADER_PADDING};
                    box-sizing: border-box;">
            <img src="{logo_path}" style="width: {Layout.LOGO_WIDTH}; height: {Layout.LOGO_HEIGHT};" />
        </div>
    '''


def build_full_page(content: str, logo_path: str | None = None) -> str:
    logo = build_logo_header(logo_path) if logo_path else ""

    return f"""
        <div style="width: {Layout.PAGE_WIDTH}; height: {Layout.PAGE_HEIGHT};
                    padding: {Layout.PAGE_PADDING}; box-sizing: border-box;
                    page-break-after: always; overflow: hidden; {Styles.FONT_BASE}">
            {logo}
            {content}
        </div>
    """


@lru_cache(maxsize=1)
def get_base_css() -> str:
    return f"""/* PDF Generator Base Styles */

@page {{
    size: {Layout.PAGE_SIZE};
    margin: 0;
}}

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    padding: 0;
    font-family: 'Inter', Arial, sans-serif;
    color: #1F2937;
}}

html, body {{
    width: 100%;
    height: 100%;
}}

table {{
    border-collapse: collapse;
    width: 100%;
}}

th, td {{
    text-align: left;
    vertical-align: top;
}}

img {{
    max-width: 100%;
    height: auto;
}}

.no-break {{
    page-break-inside: avoid;
}}

.page-break {{
    page-break-after: always;
}}

p {{
    margin: 0;
}}
"""
