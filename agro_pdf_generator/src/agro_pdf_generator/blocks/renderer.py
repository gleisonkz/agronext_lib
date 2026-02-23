from typing import Callable

from agro_pdf_generator.config import Pagination

from .schemas import BlockConfig, BlockType
from .builders import (
    build_logo,
    build_info_table,
    build_data_table,
    build_text_block,
    build_html_block,
    build_image_block,
    build_checkbox_list,
    build_signature_block,
    build_section_header,
    build_authorization_term,
    build_date_line,
    build_signature_line,
    build_date_location_line,
    build_authorization_beneficiary,
    build_lgpd_consent,
    build_proponent_declaration,
    build_federal_subsidy_term,
    build_state_subsidy_term,
    build_state_authorization_term,
)

BlockRenderer = Callable[[BlockConfig], str]


def render_block_to_html(block: BlockConfig) -> str:
    renderers: dict[BlockType, BlockRenderer] = {
        BlockType.LOGO: _render_logo,
        BlockType.INFO_TABLE: _render_info_table,
        BlockType.DATA_TABLE: _render_data_table,
        BlockType.TEXT_BLOCK: _render_text_block,
        BlockType.HTML_BLOCK: _render_html_block,
        BlockType.IMAGE: _render_image,
        BlockType.CHECKBOX: _render_checkbox,
        BlockType.SIGNATURE: _render_signature,
        BlockType.AUTHORIZATION_TERM: _render_authorization_term,
        BlockType.DATE_LINE: _render_date_line,
        BlockType.SIGNATURE_LINE: _render_signature_line,
        BlockType.DATE_LOCATION_LINE: _render_date_location_line,
        BlockType.AUTHORIZATION_BENEFICIARY: _render_authorization_beneficiary,
        BlockType.LGPD_CONSENT: _render_lgpd_consent,
        BlockType.PROPONENT_DECLARATION: _render_proponent_declaration,
        BlockType.FEDERAL_SUBSIDY_TERM: _render_federal_subsidy_term,
        BlockType.STATE_SUBSIDY_TERM: _render_state_subsidy_term,
        BlockType.STATE_AUTHORIZATION_TERM: _render_state_authorization_term,
    }

    renderer = renderers.get(block.type)
    if not renderer:
        return ""

    return renderer(block)


def render_blocks_to_pages(blocks: list[BlockConfig]) -> list[str]:
    pages: list[str] = []
    current_page: list[str] = []
    current_height = 0
    header_repeat_stopped = False  # Flag para parar repetição de headers

    # Separate blocks: repeat on all pages, repeat on range, normal
    repeat_all_blocks = [b for b in blocks if b.repeat_on_pages and not b.repeat_on_page_range]
    repeat_range_blocks = [b for b in blocks if b.repeat_on_page_range]
    normal_blocks = [b for b in blocks if not b.repeat_on_pages and not b.repeat_on_page_range]

    # Helper to get repeat content for a specific page number
    def get_repeat_html_for_page(page_num: int) -> tuple[str, int]:
        parts = []
        height = 0

        # Handle repeat_all blocks
        for block in repeat_all_blocks:
            if header_repeat_stopped:
                # Keep space but hide content
                if block.keep_space_when_hidden:
                    block_height = _calculate_block_height(block)
                    parts.append(f'<div style="height: {block_height}px;"></div>')
                    height += block_height
            else:
                block_html = render_block_to_html(block)
                if block_html:
                    parts.append(block_html)
                    height += _calculate_block_height(block)

        # Add range blocks if page is in range
        for block in repeat_range_blocks:
            if _is_page_in_range(page_num, block.repeat_on_page_range):
                if header_repeat_stopped and block.keep_space_when_hidden:
                    block_height = _calculate_block_height(block)
                    parts.append(f'<div style="height: {block_height}px;"></div>')
                    height += block_height
                elif not header_repeat_stopped:
                    block_html = _render_repeat_blocks([block])
                    if block_html:
                        parts.append(block_html)
                        height += _calculate_block_height(block)

        return "\n".join(parts), height

    # Start first page
    repeat_html, repeat_height = get_repeat_html_for_page(1)
    if repeat_html:
        current_page.append(repeat_html)
        current_height = repeat_height

    for block in normal_blocks:
        html = render_block_to_html(block)
        if not html:
            continue

        block_height = _calculate_block_height(block)

        # Force page break if requested or if block doesn't fit
        needs_break = block.force_page_break or _needs_page_break(current_height, block_height, current_page)

        if needs_break and len(current_page) > 0:
            pages.append("\n".join(current_page))
            current_page = []
            current_height = 0

            # Get repeat content for next page
            next_page_num = len(pages) + 1
            repeat_html, repeat_height = get_repeat_html_for_page(next_page_num)
            if repeat_html:
                current_page.append(repeat_html)
                current_height = repeat_height

        if block.section_header:
            current_page.append(build_section_header(block.section_header, block.section_header_pagination))

        current_page.append(html)
        current_height += block_height

        # Check if this block stops header repetition
        if block.stops_header_repeat:
            header_repeat_stopped = True

    if current_page:
        pages.append("\n".join(current_page))

    return pages


def _parse_page_range(range_str: str) -> tuple[int, int] | None:
    """Parse a page range string like '1-9' into (start, end) tuple."""
    if not range_str:
        return None

    parts = range_str.split("-")
    if len(parts) != 2:
        return None

    try:
        start = int(parts[0].strip())
        end = int(parts[1].strip())
        return (start, end)
    except ValueError:
        return None


def _is_page_in_range(page_num: int, range_str: str | None) -> bool:
    """Check if a page number is within the specified range."""
    if not range_str:
        return False

    page_range = _parse_page_range(range_str)
    if not page_range:
        return False

    start, end = page_range
    return start <= page_num <= end


def _render_repeat_blocks(blocks: list[BlockConfig]) -> str:
    if not blocks:
        return ""

    html_parts: list[str] = []
    for block in blocks:
        if block.section_header:
            html_parts.append(build_section_header(block.section_header, block.section_header_pagination))
        html = render_block_to_html(block)
        if html:
            html_parts.append(html)

    return "\n".join(html_parts)


def _calculate_block_height(block: BlockConfig) -> int:
    height = block.estimated_height
    if block.section_header:
        height += Pagination.SECTION_HEADER_HEIGHT
    return height


def _needs_page_break(current_height: int, block_height: int, current_page: list[str]) -> bool:
    return current_height + block_height > Pagination.MAX_PAGE_HEIGHT and len(current_page) > 0


## Private Renderers


def _render_logo(block: BlockConfig) -> str:
    if not block.logo_path:
        return ""
    return build_logo(block.logo_path)


def _render_info_table(block: BlockConfig) -> str:
    return build_info_table(block.rows, no_margin=block.no_margin, row_gap_after=block.row_gap_after)


def _render_data_table(block: BlockConfig) -> str:
    if not block.data_rows:
        return ""
    return build_data_table(
        headers=block.headers,
        rows=block.data_rows,
        widths=block.widths,
        variant=block.variant,
    )


def _render_text_block(block: BlockConfig) -> str:
    if not block.content:
        return ""
    return build_text_block(block.content, bordered=block.text_bordered, bold=block.text_bold)


def _render_html_block(block: BlockConfig) -> str:
    if not block.content:
        return ""
    return build_html_block(block.content)


def _render_image(block: BlockConfig) -> str:
    if not block.image_path:
        return ""
    return build_image_block(block.image_path)


def _render_checkbox(block: BlockConfig) -> str:
    if not block.checkbox_items:
        return ""
    return build_checkbox_list(block.checkbox_items, align=block.checkbox_align)


def _render_signature(block: BlockConfig) -> str:
    if not block.signatures:
        return ""
    return build_signature_block(block.signatures, date_location=block.date_location)


def _render_authorization_term(block: BlockConfig) -> str:
    if not block.authorization_term:
        return ""
    return build_authorization_term(block.authorization_term)


def _render_date_line(block: BlockConfig) -> str:
    if not block.date_text:
        return ""
    return build_date_line(block.date_text)


def _render_signature_line(block: BlockConfig) -> str:
    if not block.signature_text:
        return ""
    return build_signature_line(block.signature_text)


def _render_date_location_line(block: BlockConfig) -> str:
    if not block.date_location_label:
        return ""
    return build_date_location_line(block.date_location_label)


def _render_authorization_beneficiary(block: BlockConfig) -> str:
    if not block.authorization_beneficiary:
        return ""
    return build_authorization_beneficiary(block.authorization_beneficiary)


def _render_lgpd_consent(block: BlockConfig) -> str:
    if not block.lgpd_consent:
        return ""
    return build_lgpd_consent(block.lgpd_consent)


def _render_proponent_declaration(block: BlockConfig) -> str:
    if not block.proponent_declaration:
        return ""
    return build_proponent_declaration(block.proponent_declaration)


def _render_federal_subsidy_term(block: BlockConfig) -> str:
    if not block.federal_subsidy_term:
        return ""
    return build_federal_subsidy_term(block.federal_subsidy_term)


def _render_state_subsidy_term(block: BlockConfig) -> str:
    if not block.state_subsidy_term:
        return ""
    return build_state_subsidy_term(block.state_subsidy_term)


def _render_state_authorization_term(block: BlockConfig) -> str:
    if not block.state_authorization_term:
        return ""
    return build_state_authorization_term(block.state_authorization_term)
