from agro_pdf_generator.config import Colors, Fonts, Layout, LineHeight, Spacing, Styles

from .schemas import (
    AuthorizationBeneficiaryConfig,
    AuthorizationTermConfig,
    CheckboxAlign,
    DataTableVariant,
    FederalSubsidyTermConfig,
    LgpdConsentConfig,
    ProponentDeclarationConfig,
    StateAuthorizationTermConfig,
    StateSubsidyTermConfig,
)


def build_logo(logo_path: str) -> str:
    if not logo_path:
        return ""
    return f'''
        <div style="text-align: center; height: {Layout.LOGO_HEADER_HEIGHT};
                    padding-top: {Layout.LOGO_HEADER_PADDING}; padding-bottom: {Layout.LOGO_HEADER_PADDING};
                    box-sizing: border-box;">
            <img src="{logo_path}" style="width: {Layout.LOGO_WIDTH}; height: {Layout.LOGO_HEIGHT};" />
        </div>
    '''


def build_info_table(
    rows: list[list[dict]],
    *,
    no_margin: bool = False,
    row_gap_after: list[int] | None = None,
) -> str:
    if not rows:
        return ""

    margin_style = "" if no_margin else f"margin-bottom: {Spacing.LG};"
    gap_indices = set(row_gap_after or [])

    # Group rows by gaps
    groups: list[list[tuple[int, list[dict]]]] = []
    current_group: list[tuple[int, list[dict]]] = []

    for i, row in enumerate(rows):
        current_group.append((i, row))
        if i in gap_indices:
            groups.append(current_group)
            current_group = []

    if current_group:
        groups.append(current_group)

    # Build HTML for each group
    groups_html = []
    for group_idx, group in enumerate(groups):
        rows_html = []
        for row_idx, (i, row) in enumerate(group):
            is_last_row_in_group = row_idx == len(group) - 1

            border_style = (
                ""
                if is_last_row_in_group
                else f"border-bottom: 1px solid {Colors.BORDER};"
            )

            cells_html = []
            for j, cell in enumerate(row):
                label = cell.get("label", "")
                value = cell.get("value", "")
                width = cell.get("width", "auto")
                background_color = cell.get("background_color", "")
                text_color = cell.get("text_color", "")

                is_last_cell = j == len(row) - 1
                cell_border = (
                    "" if is_last_cell else f"border-right: 1px solid {Colors.BORDER};"
                )

                # Custom background and text colors for special cells
                bg_style = (
                    f"background: {background_color};" if background_color else ""
                )

                # Override label and value styles if text_color is provided
                if text_color:
                    label_style = f"font-family: {Fonts.FAMILY}; font-size: {Fonts.SIZE_MEDIUM}; font-weight: {Fonts.WEIGHT_SEMIBOLD}; line-height: {LineHeight.NORMAL}; color: {text_color};"
                    # Special styled cell: bold, centered
                    value_style = f"font-family: {Fonts.FAMILY}; font-size: {Fonts.SIZE_MEDIUM}; font-weight: {Fonts.WEIGHT_SEMIBOLD}; line-height: {LineHeight.NORMAL}; color: {text_color}; word-break: break-word; text-align: center;"
                    # Use centered flex layout for special cells
                    cell_layout = f"flex: 0 0 {width}; max-width: {width}; {Styles.INFO_CELL} {cell_border} {bg_style} justify-content: center; align-items: center;"
                    cells_html.append(f'''
                    <div style="{cell_layout}">
                        <span style="{value_style}">{value}</span>
                    </div>
                ''')
                else:
                    label_style = Styles.LABEL
                    value_style = f"{Styles.VALUE} word-break: break-word;"
                    cells_html.append(f'''
                    <div style="flex: 0 0 {width}; max-width: {width}; {Styles.INFO_CELL} {cell_border} {bg_style}">
                        <span style="{label_style}">{label}</span>
                        <span style="{value_style}">{value}</span>
                    </div>
                ''')

            rows_html.append(f'''
                <div style="{Styles.INFO_ROW} {border_style}">
                    {"".join(cells_html)}
                </div>
            ''')

        # Add margin-bottom to all groups except the last
        group_margin = (
            f"margin-bottom: {Spacing.XS};" if group_idx < len(groups) - 1 else ""
        )

        groups_html.append(f"""
            <div style="border: 1px solid {Colors.BORDER}; border-radius: {Layout.BORDER_RADIUS}; overflow: hidden; {group_margin}">
                {"".join(rows_html)}
            </div>
        """)

    return f'''
        <div style="{margin_style}">
            {"".join(groups_html)}
        </div>
    '''


def build_data_table(
    headers: list[str],
    rows: list[list[str]],
    widths: list[str] | None = None,
    variant: DataTableVariant = DataTableVariant.DEFAULT,
) -> str:
    if not rows:
        return ""

    col_count = len(headers) if headers else (len(rows[0]) if rows else 0)
    if not col_count:
        return ""

    effective_widths = widths or ["auto"] * col_count

    # Determine styles based on variant
    use_small_font = variant in (
        DataTableVariant.SMALL_CENTERED_UPPERCASE,
        DataTableVariant.SMALL_CENTERED_NORMAL,
    )
    use_uppercase = variant in (
        DataTableVariant.CENTERED_UPPERCASE,
        DataTableVariant.SMALL_CENTERED_UPPERCASE,
    )
    use_centered = variant != DataTableVariant.DEFAULT

    header_style = Styles.TABLE_HEADER_SMALL if use_small_font else Styles.TABLE_HEADER
    cell_style = Styles.TABLE_CELL_SMALL if use_small_font else Styles.TABLE_CELL
    cell_align = "text-align: center;" if use_centered else ""
    header_transform = "text-transform: uppercase;" if use_uppercase else ""
    word_wrap = "word-wrap: break-word; overflow-wrap: break-word;"

    # Cell padding: 8px all sides
    cell_padding = f"padding: {Spacing.MD};"

    header_html = ""
    if headers:
        header_cells = []
        for i, h in enumerate(headers):
            width = effective_widths[i] if i < len(effective_widths) else "auto"
            is_last_cell = i == len(headers) - 1
            border_right = (
                "" if is_last_cell else f"border-right: 1px solid {Colors.BORDER};"
            )
            header_cells.append(f'''
                <th style="{header_style} text-align: center; vertical-align: middle; {header_transform} {word_wrap} {cell_padding} width: {width}; border-bottom: 1px solid {Colors.BORDER}; {border_right}">
                    {h}
                </th>
            ''')
        header_html = f"<tr>{''.join(header_cells)}</tr>"

    rows_html = []
    for row_idx, row in enumerate(rows):
        is_last_row = row_idx == len(rows) - 1
        cells = []
        for i, cell in enumerate(row):
            width = effective_widths[i] if i < len(effective_widths) else "auto"
            is_last_cell = i == len(row) - 1
            border_bottom = (
                "" if is_last_row else f"border-bottom: 1px solid {Colors.BORDER};"
            )
            border_right = (
                "" if is_last_cell else f"border-right: 1px solid {Colors.BORDER};"
            )
            cells.append(f'''
                <td style="{cell_style} {cell_align} {word_wrap} {cell_padding} width: {width}; vertical-align: middle; {border_bottom} {border_right}">
                    {cell}
                </td>
            ''')
        rows_html.append(f"<tr>{''.join(cells)}</tr>")

    return f'''
        <div style="{Styles.BORDERED_CONTAINER} margin-bottom: {Spacing.LG};">
            <table style="width: 100%; border-collapse: collapse; table-layout: fixed;">
                {header_html}
                {"".join(rows_html)}
            </table>
        </div>
    '''


def build_text_block(content: str, *, bordered: bool = True, bold: bool = False) -> str:
    if not content:
        return ""

    container_style = (
        f"{Styles.BORDERED_CONTAINER} padding: {Spacing.MD};" if bordered else ""
    )
    font_weight = f"font-weight: {Fonts.WEIGHT_SEMIBOLD};" if bold else ""

    return f'''
        <div style="{container_style} margin-bottom: {Spacing.LG};">
            <p style="{Styles.VALUE} {font_weight} margin: 0; white-space: pre-wrap;">{content}</p>
        </div>
    '''


def build_html_block(content: str) -> str:
    if not content:
        return ""

    return f'''
        <div style="{Styles.HTML_BLOCK_TEXT} margin-bottom: {Spacing.LG}; padding: 0 {Spacing.LG}; box-sizing: border-box;">
            <style>
                .html-block p {{ margin: 0 0 {Spacing.MD} 0; }}
                .html-block p:last-child {{ margin-bottom: 0; }}
                .html-block a {{ color: inherit; text-decoration: underline; }}
            </style>
            <div class="html-block">
                {content}
            </div>
        </div>
    '''


def build_image_block(image_path: str) -> str:
    if not image_path:
        return ""

    return f'''
        <div style="{Styles.BORDERED_CONTAINER} padding: {Spacing.MD}; margin-bottom: {Spacing.LG};">
            <img src="{image_path}" style="width: 100%; display: block;" />
        </div>
    '''


def build_checkbox_item(
    label: str,
    checked: bool = False,
    align: CheckboxAlign = CheckboxAlign.TOP,
    bold: bool = False,
    font_size: str | None = None,
) -> str:
    checkbox_style = Styles.CHECKBOX_CHECKED if checked else Styles.CHECKBOX_UNCHECKED
    align_style = (
        "align-items: flex-start;"
        if align == CheckboxAlign.TOP
        else "align-items: center;"
    )
    bold_style = f"font-weight: {Fonts.WEIGHT_SEMIBOLD};" if bold else ""

    # Use custom font size if provided, otherwise use Styles.VALUE
    if font_size:
        text_style = f"font-family: {Fonts.FAMILY}; font-size: {font_size}; font-weight: {Fonts.WEIGHT_NORMAL}; line-height: {LineHeight.NORMAL}; color: {Colors.PRIMARY};"
    else:
        text_style = Styles.VALUE

    checkmark = (
        """<svg width="10" height="8" viewBox="0 0 10 8" fill="none" style="display: block; margin: auto;">
        <path d="M1 4L3.5 6.5L9 1" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>"""
        if checked
        else ""
    )

    return f'''
        <div style="display: flex; gap: {Spacing.MD}; {align_style} margin-bottom: {Spacing.SM};">
            <div style="{checkbox_style}">{checkmark}</div>
            <span style="{text_style} {bold_style}">{label}</span>
        </div>
    '''


def build_checkbox_list(
    items: list[dict], align: CheckboxAlign = CheckboxAlign.TOP
) -> str:
    if not items:
        return ""

    checkboxes = [
        build_checkbox_item(item.get("label", ""), item.get("checked", False), align)
        for item in items
    ]

    return f'''
        <div style="{Styles.BORDERED_CONTAINER} padding: {Spacing.MD}; margin-bottom: {Spacing.LG};">
            {"".join(checkboxes)}
        </div>
    '''


def build_signature_block(signatures: list[dict], *, date_location: str = "") -> str:
    if not signatures:
        return ""

    sig_html = []
    for sig in signatures:
        title = sig.get("title", "")
        name = sig.get("name", "")
        sig_html.append(f'''
            <div style="flex: 1; text-align: center;">
                <div style="border-top: 1px solid {Colors.BORDER}; padding-top: {Spacing.SM}; margin: 0 {Spacing.LG};">
                    <p style="{Styles.SIGNATURE_TEXT} margin: 0; font-weight: {Fonts.WEIGHT_SEMIBOLD};">{title}</p>
                    <p style="{Styles.SIGNATURE_TEXT} margin: {Spacing.XS} 0 0 0;">{name}</p>
                </div>
            </div>
        ''')

    date_html = ""
    if date_location:
        date_html = f'''
            <p style="{Styles.SIGNATURE_TEXT} text-align: center; margin-bottom: {Spacing.LG};">
                {date_location}
            </p>
        '''

    return f"""
        <div style="margin-top: {Spacing.XL}; margin-bottom: {Spacing.LG};">
            {date_html}
            <div style="display: flex; gap: {Spacing.LG};">
                {"".join(sig_html)}
            </div>
        </div>
    """


def build_section_header(title: str, show_pagination: bool = False) -> str:
    if not title:
        return ""

    pagination_html = ""
    if show_pagination:
        pagination_html = f"""
            <span style="font-family: {Fonts.FAMILY}; font-size: {Fonts.SIZE_MEDIUM};
                        font-weight: {Fonts.WEIGHT_SEMIBOLD}; line-height: {LineHeight.NORMAL};
                        color: {Colors.PRIMARY}; white-space: nowrap;">Página</span>
            <span style="font-family: {Fonts.FAMILY}; font-size: {Fonts.SIZE_MEDIUM};
                        font-weight: {Fonts.WEIGHT_NORMAL}; line-height: {LineHeight.NORMAL};
                        color: {Colors.PRIMARY}; white-space: nowrap;">{{{{page}}}}</span>
        """

    return f"""
        <div style="border: 1px solid {Colors.BORDER}; border-radius: {Layout.BORDER_RADIUS};
                    min-height: 32px; padding: {Spacing.MD}; margin-bottom: {Spacing.MD}; box-sizing: border-box;">
            <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
                <span style="font-family: {Fonts.FAMILY}; font-size: {Fonts.SIZE_MEDIUM};
                            font-weight: {Fonts.WEIGHT_SEMIBOLD}; line-height: {LineHeight.NORMAL};
                            color: {Colors.PRIMARY}; white-space: normal; word-wrap: break-word;">{title}</span>
                <div style="flex: 1; height: 1px; background: {Colors.BORDER}; min-width: 80px;"></div>
                {pagination_html}
            </div>
        </div>
    """


def build_section_second_header(title: str) -> str:
    if not title:
        return ""

    return f"""
        <div style="border: 1px solid {Colors.BORDER}; border-radius: {Layout.BORDER_RADIUS};
                    min-height: 32px; padding: {Spacing.MD}; margin-bottom: {Spacing.MD}; box-sizing: border-box;">
            <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
                <span style="font-family: {Fonts.FAMILY}; font-size: {Fonts.SIZE_MEDIUM};
                            font-weight: {Fonts.WEIGHT_NORMAL}; line-height: {LineHeight.NORMAL};
                            color: {Colors.PRIMARY}; white-space: normal; word-wrap: break-word;">{title}</span>
                <div style="flex: 1; height: 1px; background: {Colors.BORDER}; min-width: 80px;"></div>
            </div>
        </div>
    """


def build_authorization_term(data: AuthorizationTermConfig) -> str:
    if not data:
        return ""

    # Build fields (label: value) - supports inline for same line
    fields_html = ""
    current_line = ""
    fields = data.get("fields", [])

    for i, field in enumerate(fields):
        label = field.get("label", "")
        value = field.get("value", "")
        is_inline = field.get("inline", False)

        field_content = f'<span style="font-weight: {Fonts.WEIGHT_SEMIBOLD};">{label}:</span> {value}'

        if is_inline:
            # Add to current line with spacing
            current_line += f" &nbsp;&nbsp;&nbsp; {field_content}"
        else:
            # Close previous line if exists
            if current_line:
                fields_html += f"""
            <div style="margin-bottom: {Spacing.MD};">
                {current_line}
            </div>
        """
            current_line = field_content

    # Close last line
    if current_line:
        fields_html += f"""
            <div style="margin-bottom: {Spacing.MD};">
                {current_line}
            </div>
        """

    # Intro text
    intro_text = data.get("intro_text", "")
    intro_html = (
        f"""
        <div style="margin-bottom: {Spacing.LG};">
            {intro_text}
        </div>
    """
        if intro_text
        else ""
    )

    # Build sections (title + text)
    sections_html = ""
    for section in data.get("sections", []):
        title = section.get("title", "")
        text = section.get("text", "")
        if title:
            sections_html += f"""
                <div style="margin-bottom: {Spacing.MD}; font-weight: {Fonts.WEIGHT_SEMIBOLD};">{title}:</div>
            """
        sections_html += f"""
            <div style="margin-bottom: {Spacing.LG};">
                {text}
            </div>
        """

    # Closing text (centered - e.g., "Firmo...", with 24px margin before)
    closing_text = data.get("closing_text", "")
    closing_html = (
        f"""
        <div style="text-align: center; margin-top: {Spacing.XXL}; margin-bottom: {Spacing.LG};">
            {closing_text}
        </div>
    """
        if closing_text
        else ""
    )

    # Date line (uses DATE_LINE component internally)
    date_text = data.get("date_text", "")
    date_html = build_date_line(date_text) if date_text else ""

    # Signature (uses SIGNATURE_LINE component internally)
    signature_text = data.get("signature_text", "")
    signature_html = build_signature_line(signature_text) if signature_text else ""

    return f"""
        <div style="font-family: {Fonts.FAMILY}; font-size: {Fonts.SIZE_LARGE}; line-height: 1.4; color: {Colors.PRIMARY}; margin-bottom: {Spacing.LG};">
            {fields_html}
            {intro_html}
            {sections_html}
            {closing_html}
            {date_html}
            {signature_html}
        </div>
    """


def build_date_line(text: str) -> str:
    if not text:
        return ""

    return f"""
        <div style="font-family: {Fonts.FAMILY}; font-size: {Fonts.SIZE_LARGE}; color: {Colors.PRIMARY}; margin-bottom: {Spacing.LG}; text-align: center;">
            {text}
        </div>
    """


def build_signature_line(text: str) -> str:
    if not text:
        return ""

    return f"""
        <div style="text-align: center; margin-top: 40px; margin-bottom: {Spacing.LG};">
            <div style="border-top: 1px solid {Colors.BORDER}; width: 400px; margin: 0 auto; padding-top: {Spacing.MD};
                        font-family: {Fonts.FAMILY}; font-size: {Fonts.SIZE_LARGE}; color: {Colors.PRIMARY};">
                {text}
            </div>
        </div>
    """


def build_date_location_line(label: str) -> str:
    if not label:
        return ""

    return f"""
        <div style="text-align: center; margin-top: {Spacing.LG}; margin-bottom: {Spacing.MD};">
            <div style="font-family: {Fonts.FAMILY}; font-size: 16px; color: {Colors.PRIMARY}; margin-bottom: 4px;">
                _______________________________, ____ de _____________ de ________.
            </div>
            <div style="font-family: {Fonts.FAMILY}; font-size: 16px; color: {Colors.PRIMARY};">
                {label}
            </div>
        </div>
    """


def _build_fields_html(fields: list, spacing: str) -> str:
    """Helper to build fields HTML with inline and gap_before support."""
    fields_html = ""
    current_line = ""

    for field in fields:
        label = field.get("label", "")
        value = field.get("value", "")
        is_inline = field.get("inline", False)
        gap_before = field.get("gap_before", False)

        field_content = f'<span style="font-weight: {Fonts.WEIGHT_SEMIBOLD};">{label}:</span> {value}'

        if is_inline:
            current_line += f" &nbsp;&nbsp;&nbsp; {field_content}"
        else:
            if current_line:
                # Use gap if the CURRENT field (next line) has gap_before
                margin = Spacing.LG if gap_before else spacing
                fields_html += f"""
            <div style="margin-bottom: {margin};">
                {current_line}
            </div>
        """
            current_line = field_content

    if current_line:
        fields_html += f"""
            <div style="margin-bottom: {spacing};">
                {current_line}
            </div>
        """

    return fields_html


def build_authorization_beneficiary(data: AuthorizationBeneficiaryConfig) -> str:
    if not data:
        return ""

    # Initial fields (Nome do beneficiário, Número da proposta)
    initial_fields_html = _build_fields_html(data.get("initial_fields", []), Spacing.MD)

    # Authorization checkbox question and answer
    auth_question = data.get("authorization_question", "")
    auth_answer = data.get("authorization_answer", "")
    auth_checkbox_html = ""
    if auth_question:
        auth_checkbox_html = f"""
            <div style="margin-bottom: {Spacing.MD}; font-weight: {Fonts.WEIGHT_SEMIBOLD};">
                {auth_question}
            </div>
            <div style="margin-bottom: {Spacing.MD};">
                Resposta: {auth_answer}
            </div>
        """

    # Authorization text (bold with lines above and below)
    auth_text = data.get("authorization_text", "")
    auth_text_html = (
        f"""
        <div style="border-top: 1px solid {Colors.BORDER}; border-bottom: 1px solid {Colors.BORDER}; padding: {Spacing.MD} 0; margin-bottom: {Spacing.LG}; font-weight: {Fonts.WEIGHT_SEMIBOLD};">
            {auth_text}
        </div>
    """
        if auth_text
        else ""
    )

    # Beneficiary fields
    beneficiary_fields_html = _build_fields_html(
        data.get("beneficiary_fields", []), Spacing.MD
    )

    # Observation text (italic)
    observation_text = data.get("observation_text", "")
    observation_html = (
        f"""
        <div style="margin-bottom: {Spacing.LG}; font-style: italic;">
            {observation_text}
        </div>
    """
        if observation_text
        else ""
    )

    # Sections (Quitação, Isenção)
    sections_html = ""
    for section in data.get("sections", []):
        title = section.get("title", "")
        text = section.get("text", "")
        if title:
            sections_html += f"""
                <div style="margin-bottom: {Spacing.MD}; font-weight: {Fonts.WEIGHT_SEMIBOLD};">{title}:</div>
            """
        sections_html += f"""
            <div style="margin-bottom: {Spacing.LG};">
                {text}
            </div>
        """

    # Closing text (centered, with 24px margin before)
    closing_text = data.get("closing_text", "")
    closing_html = (
        f"""
        <div style="text-align: center; margin-top: {Spacing.XXL}; margin-bottom: {Spacing.LG};">
            {closing_text}
        </div>
    """
        if closing_text
        else ""
    )

    # Date and signature
    date_text = data.get("date_text", "")
    date_html = build_date_line(date_text) if date_text else ""

    signature_text = data.get("signature_text", "")
    signature_html = build_signature_line(signature_text) if signature_text else ""

    # Footer OBS
    footer_obs = data.get("footer_obs", [])
    footer_html = ""
    if footer_obs:
        footer_html = f'<div style="margin-top: {Spacing.LG};">'
        footer_html += f'<div style="margin-bottom: {Spacing.SM};">OBS:</div>'
        for obs in footer_obs:
            footer_html += f'<div style="margin-bottom: {Spacing.XS};">- {obs}</div>'
        footer_html += "</div>"

    return f"""
        <div style="font-family: {Fonts.FAMILY}; font-size: {Fonts.SIZE_LARGE}; line-height: 1.4; color: {Colors.PRIMARY}; margin-bottom: {Spacing.LG};">
            {initial_fields_html}
            {auth_checkbox_html}
            {auth_text_html}
            {beneficiary_fields_html}
            {observation_html}
            {sections_html}
            {closing_html}
            {date_html}
            {signature_html}
            {footer_html}
        </div>
    """


def build_lgpd_consent(data: LgpdConsentConfig) -> str:
    if not data:
        return ""

    # Title (centered, not bold)
    title = data.get("title", "")
    title_html = (
        f"""
        <div style="text-align: center; margin-bottom: {Spacing.LG};">
            {title}
        </div>
    """
        if title
        else ""
    )

    # Consent text (centered)
    consent_text = data.get("consent_text", "")
    consent_html = (
        f"""
        <div style="text-align: center; margin-bottom: {Spacing.LG};">
            {consent_text}
        </div>
    """
        if consent_text
        else ""
    )

    # Signature line
    signature_text = data.get("signature_text", "")
    signature_html = (
        f"""
        <div style="text-align: center; margin-top: 40px;">
            <div style="border-top: 1px solid {Colors.BORDER}; width: 400px; margin: 0 auto; padding-top: {Spacing.MD};
                        font-family: {Fonts.FAMILY}; font-size: {Fonts.SIZE_LARGE}; color: {Colors.PRIMARY};">
                {signature_text}
            </div>
        </div>
    """
        if signature_text
        else ""
    )

    return f"""
        <div style="font-family: {Fonts.FAMILY}; font-size: {Fonts.SIZE_LARGE}; line-height: 1.4; color: {Colors.PRIMARY}; margin-bottom: {Spacing.LG};">
            {title_html}
            {consent_html}
            {signature_html}
        </div>
    """


def build_proponent_declaration(data: ProponentDeclarationConfig) -> str:
    if not data:
        return ""

    # HTML content
    content_html = data.get("content_html", "")
    content_bold = data.get("content_bold", False)
    bold_style = f"font-weight: {Fonts.WEIGHT_SEMIBOLD};" if content_bold else ""
    # Add style for p tags with 13px gap
    content_block = (
        f"""
        <div style="margin-bottom: {Spacing.LG}; {bold_style}">
            <style>
                .proponent-content p {{ margin: 0 0 13px 0; }}
                .proponent-content p:last-child {{ margin-bottom: 0; }}
            </style>
            <div class="proponent-content">
                {content_html}
            </div>
        </div>
    """
        if content_html
        else ""
    )

    # Checkbox with text (only if checkbox_text is provided)
    checkbox_text = data.get("checkbox_text", "")
    checkbox_checked = data.get("checkbox_checked", False)
    checkbox_align_str = data.get("checkbox_align", "top")
    checkbox_align = (
        CheckboxAlign.CENTER if checkbox_align_str == "center" else CheckboxAlign.TOP
    )
    checkbox_bold = data.get("checkbox_bold", False)
    checkbox_html = ""
    if checkbox_text:
        checkbox_html = f"""
            <div style="margin-bottom: {Spacing.LG};">
                {build_checkbox_item(checkbox_text, checkbox_checked, checkbox_align, checkbox_bold, font_size="16px")}
            </div>
        """

    # Triple signature (3 columns with vertical dividers)
    triple_sig = data.get("triple_signature", {})
    triple_sig_html = ""
    if triple_sig:
        left_label = triple_sig.get("left_label", "")
        center_label = triple_sig.get("center_label", "")
        right_label = triple_sig.get("right_label", "")

        triple_sig_style = f"font-family: {Fonts.FAMILY}; font-weight: 400; font-size: 14px; line-height: 14px; text-align: center; color: {Colors.PRIMARY};"

        triple_sig_html = f'''
            <div style="display: flex; margin-top: {Spacing.XL}; margin-bottom: {Spacing.LG}; border-top: 1px solid {Colors.BORDER}; border-bottom: 1px solid {Colors.BORDER}; height: 58px;">
                <div style="flex: 1; text-align: center; padding-top: 8px;">
                    <span style="{triple_sig_style}">{left_label}</span>
                </div>
                <div style="width: 1px; background: {Colors.BORDER}; margin-top: 8px; margin-bottom: 4px;"></div>
                <div style="flex: 1; text-align: center; padding-top: 8px;">
                    <span style="{triple_sig_style}">{center_label}</span>
                </div>
                <div style="width: 1px; background: {Colors.BORDER}; margin-top: 8px; margin-bottom: 4px;"></div>
                <div style="flex: 1; text-align: center; padding-top: 8px;">
                    <span style="{triple_sig_style}">{right_label}</span>
                </div>
            </div>
        '''

    # Observation text (small, right aligned)
    observation_text = data.get("observation_text", "")
    observation_html = (
        f"""
        <div style="font-family: {Fonts.FAMILY}; font-size: 12px; color: {Colors.PRIMARY}; margin-bottom: {Spacing.LG}; text-align: right; margin-right: 16px;">
            {observation_text}
        </div>
    """
        if observation_text
        else ""
    )

    # Footer bordered text
    footer_bordered_text = data.get("footer_bordered_text", "")
    footer_style = f"font-family: {Fonts.FAMILY}; font-size: 16px; font-weight: 400; line-height: 20px; color: {Colors.PRIMARY};"
    footer_html = (
        f'''
        <div style="{Styles.BORDERED_CONTAINER} padding: {Spacing.MD};">
            <span style="{footer_style}">{footer_bordered_text}</span>
        </div>
    '''
        if footer_bordered_text
        else ""
    )

    return f"""
        <div style="font-family: {Fonts.FAMILY}; font-size: {Fonts.SIZE_LARGE}; line-height: 1.4; color: {Colors.PRIMARY}; margin-bottom: {Spacing.LG};">
            {content_block}
            {checkbox_html}
            {triple_sig_html}
            {observation_html}
            {footer_html}
        </div>
    """


def build_federal_subsidy_term(data: FederalSubsidyTermConfig) -> str:
    if not data:
        return ""

    # Header do Ministério
    ministry_header = data.get("ministry_header", "")
    committee_text = data.get("committee_text", "")
    secretariat_text = data.get("secretariat_text", "")
    main_title = data.get("main_title", "")

    header_html = ""
    if ministry_header:
        header_html = f"""
            <div style="text-align: center; margin-bottom: {Spacing.LG};">
                <div style="font-family: {Fonts.FAMILY}; font-size: 16px; font-weight: 600; color: {Colors.PRIMARY}; margin-bottom: 4px;">
                    {ministry_header}
                </div>
                <div style="font-family: {Fonts.FAMILY}; font-size: 16px; color: {Colors.PRIMARY}; margin-bottom: 2px;">
                    {committee_text}
                </div>
                <div style="font-family: {Fonts.FAMILY}; font-size: 16px; color: {Colors.PRIMARY}; margin-bottom: {Spacing.MD};">
                    {secretariat_text}
                </div>
                <div style="font-family: {Fonts.FAMILY}; font-size: 16px; font-weight: 600; color: {Colors.PRIMARY};">
                    {main_title}
                </div>
            </div>
        """

    # Seção título e intro
    section_title = data.get("section_title", "")
    intro_text = data.get("intro_text", "")

    section_html = (
        f"""
        <div style="margin-bottom: {Spacing.MD};">
            <div style="font-family: {Fonts.FAMILY}; font-size: 16px; color: {Colors.PRIMARY}; margin-bottom: {Spacing.LG};">
                {section_title}
            </div>
            <div style="font-family: {Fonts.FAMILY}; font-size: 16px; color: {Colors.PRIMARY}; margin-bottom: {Spacing.MD};">
                {intro_text}
            </div>
        </div>
    """
        if section_title
        else ""
    )

    # Modalidades com formato a) ( )
    modality_options = data.get("modality_options", [])
    modality_html = ""
    if modality_options:
        items_html = ""
        letters = "abcdefghijklmnopqrstuvwxyz"
        for i, opt in enumerate(modality_options):
            label = opt.get("label", "")
            checked = opt.get("checked", False)
            letter = letters[i] if i < len(letters) else str(i + 1)
            items_html += f"""
                <div style="font-family: {Fonts.FAMILY}; font-size: 16px; color: {Colors.PRIMARY}; margin-bottom: 4px;">
                    {letter}) ({"X" if checked else " "}) {label}
                </div>
            """
        modality_html = f'<div style="margin-bottom: {Spacing.MD};">{items_html}</div>'

    # Texto antes das declarações
    declaration_intro = data.get("declaration_intro", "")
    declaration_intro_html = (
        f"""
        <div style="font-family: {Fonts.FAMILY}; font-size: 16px; color: {Colors.PRIMARY}; margin-bottom: {Spacing.MD};">
            {declaration_intro}
        </div>
    """
        if declaration_intro
        else ""
    )

    # Lista de declarações
    declarations = data.get("declarations", [])
    declarations_html = ""
    if declarations:
        items_html = ""
        for decl in declarations:
            items_html += f"""
                <div style="font-family: {Fonts.FAMILY}; font-size: 16px; color: {Colors.PRIMARY}; margin-bottom: 16px;">
                    {decl}
                </div>
            """
        declarations_html = (
            f'<div style="margin-bottom: {Spacing.LG};">{items_html}</div>'
        )

    # Data e assinatura
    signature_date_text = data.get("signature_date_text", "")
    signature_text = data.get("signature_text", "")

    signature_html = (
        f"""
        <div style="margin-top: {Spacing.XL};">
            <div style="font-family: {Fonts.FAMILY}; font-size: 16px; color: {Colors.PRIMARY}; margin-bottom: {Spacing.LG};">
                {signature_date_text}
            </div>
            <div style="font-family: {Fonts.FAMILY}; font-size: 16px; color: {Colors.PRIMARY};">
                {signature_text}
            </div>
        </div>
    """
        if signature_date_text or signature_text
        else ""
    )

    # Seção II
    section2_title = data.get("section2_title", "")
    section2_question = data.get("section2_question", "")
    section2_options = data.get("section2_options", [])
    section2_date_text = data.get("section2_date_text", "")
    section2_responsible_text = data.get("section2_responsible_text", "")
    section2_cpf_text = data.get("section2_cpf_text", "")
    section2_signature_text = data.get("section2_signature_text", "")

    section2_html = ""
    if section2_title:
        # Título da seção II
        section2_html += f"""
            <div style="font-family: {Fonts.FAMILY}; font-size: 16px; font-weight: 600; color: {Colors.PRIMARY}; margin-bottom: {Spacing.MD};">
                {section2_title}
            </div>
        """

        # Pergunta
        if section2_question:
            section2_html += f"""
                <div style="font-family: {Fonts.FAMILY}; font-size: 16px; color: {Colors.PRIMARY}; margin-bottom: 24px;">
                    {section2_question}
                </div>
            """

        # Opções
        if section2_options:
            options_html = ""
            for opt in section2_options:
                options_html += f"""
                    <div style="font-family: {Fonts.FAMILY}; font-size: 16px; color: {Colors.PRIMARY}; margin-bottom: 4px;">
                        ( ) {opt}
                    </div>
                """
            section2_html += f'<div style="margin-bottom: 24px;">{options_html}</div>'

        # Data
        if section2_date_text:
            section2_html += f"""
                <div style="font-family: {Fonts.FAMILY}; font-size: 16px; color: {Colors.PRIMARY}; margin-bottom: {Spacing.SM};">
                    {section2_date_text}
                </div>
            """

        # Responsável
        if section2_responsible_text:
            section2_html += f"""
                <div style="font-family: {Fonts.FAMILY}; font-size: 16px; color: {Colors.PRIMARY}; margin-bottom: {Spacing.SM};">
                    {section2_responsible_text}
                </div>
            """

        # CPF
        if section2_cpf_text:
            section2_html += f"""
                <div style="font-family: {Fonts.FAMILY}; font-size: 16px; color: {Colors.PRIMARY}; margin-bottom: {Spacing.SM};">
                    {section2_cpf_text}
                </div>
            """

        # Assinatura
        if section2_signature_text:
            section2_html += f"""
                <div style="font-family: {Fonts.FAMILY}; font-size: 16px; color: {Colors.PRIMARY};">
                    {section2_signature_text}
                </div>
            """

    return f"""
        <div style="font-family: {Fonts.FAMILY}; font-size: 16px; color: {Colors.PRIMARY}; margin-top: 16px; margin-bottom: {Spacing.LG};">
            {header_html}
            {section_html}
            {modality_html}
            {declaration_intro_html}
            {declarations_html}
            {signature_html}
            {section2_html}
        </div>
    """


def build_state_subsidy_term(data: StateSubsidyTermConfig) -> str:
    if not data:
        return ""

    government_header = data.get("government_header", "")
    annex_title = data.get("annex_title", "")
    intro_text = data.get("intro_text", "")
    declarations = data.get("declarations", [])
    date_location_text = data.get("date_location_text", "")
    signature_text = data.get("signature_text", "")
    name_cpf_text = data.get("name_cpf_text", "")

    # Header do governo
    header_html = ""
    if government_header:
        header_html = f"""
            <div style="text-align: center; margin-bottom: 24px;">
                <div style="font-family: {Fonts.FAMILY}; font-size: 16px; font-weight: 600; color: {Colors.PRIMARY};">
                    {government_header}
                </div>
            </div>
        """

    # Título do anexo
    annex_html = ""
    if annex_title:
        annex_html = f"""
            <div style="text-align: center; margin-bottom: {Spacing.LG};">
                <div style="font-family: {Fonts.FAMILY}; font-size: 16px; font-weight: 600; color: {Colors.PRIMARY};">
                    {annex_title}
                </div>
            </div>
        """

    # Texto introdutório
    intro_html = ""
    if intro_text:
        intro_html = f"""
            <div style="font-family: {Fonts.FAMILY}; font-size: 16px; color: {Colors.PRIMARY}; margin-bottom: {Spacing.MD}; text-align: justify;">
                {intro_text}
            </div>
        """

    # Declarações numeradas
    declarations_html = ""
    if declarations:
        items_html = ""
        for decl in declarations:
            items_html += f"""
                <div style="font-family: {Fonts.FAMILY}; font-size: 16px; color: {Colors.PRIMARY}; margin-bottom: {Spacing.MD}; text-align: justify;">
                    {decl}
                </div>
            """
        declarations_html = (
            f'<div style="margin-bottom: {Spacing.MD};">{items_html}</div>'
        )

    # Data e local - usa o componente
    date_location_html = (
        build_date_location_line(date_location_text) if date_location_text else ""
    )

    # Linha de assinatura
    signature_html = ""
    if signature_text:
        signature_html = f"""
            <div style="text-align: center; margin-top: {Spacing.LG}; margin-bottom: {Spacing.SM};">
                <div style="font-family: {Fonts.FAMILY}; font-size: 16px; color: {Colors.PRIMARY}; border-top: 1px solid {Colors.BORDER}; display: inline-block; padding-top: {Spacing.SM}; min-width: 300px;">
                    {signature_text}
                </div>
            </div>
        """

    # Nome e CPF
    name_cpf_html = ""
    if name_cpf_text:
        name_cpf_html = f"""
            <div style="text-align: center;">
                <div style="font-family: {Fonts.FAMILY}; font-size: 16px; color: {Colors.PRIMARY};">
                    {name_cpf_text}
                </div>
            </div>
        """

    return f"""
        <div style="font-family: {Fonts.FAMILY}; font-size: 16px; color: {Colors.PRIMARY}; margin-top: 16px;">
            {header_html}
            {annex_html}
            {intro_html}
            {declarations_html}
            {date_location_html}
            {signature_html}
            {name_cpf_html}
        </div>
    """


def build_state_authorization_term(data: StateAuthorizationTermConfig) -> str:
    if not data:
        return ""

    logo_path = data.get("logo_path", "")
    government_header = data.get("government_header", "")
    government_subheader = data.get("government_subheader", "")
    annex_title = data.get("annex_title", "")
    intro_text = data.get("intro_text", "")
    declarations = data.get("declarations", [])
    date_location_text = data.get("date_location_text", "")
    signature_text = data.get("signature_text", "")
    name_cpf_text = data.get("name_cpf_text", "")

    # Header com logo do governo
    header_html = ""
    if logo_path or government_header:
        logo_html = ""
        if logo_path:
            logo_html = f'''
                <img src="{logo_path}" style="height: 80px; margin-bottom: 8px;" />
            '''

        subheader_html = ""
        if government_subheader:
            subheader_html = f"""
                <div style="font-family: {Fonts.FAMILY}; font-size: 12px; color: {Colors.PRIMARY};">
                    {government_subheader}
                </div>
            """

        header_html = f"""
            <div style="text-align: center; margin-bottom: 24px;">
                {logo_html}
                <div style="font-family: {Fonts.FAMILY}; font-size: 14px; font-weight: 600; color: {Colors.PRIMARY};">
                    {government_header}
                </div>
                {subheader_html}
            </div>
        """

    # Título do anexo
    annex_html = ""
    if annex_title:
        annex_html = f"""
            <div style="text-align: center; margin-bottom: {Spacing.LG};">
                <div style="font-family: {Fonts.FAMILY}; font-size: 16px; font-weight: 600; color: {Colors.PRIMARY};">
                    {annex_title}
                </div>
            </div>
        """

    # Texto introdutório
    intro_html = ""
    if intro_text:
        intro_html = f"""
            <div style="font-family: {Fonts.FAMILY}; font-size: 16px; color: {Colors.PRIMARY}; margin-bottom: {Spacing.MD}; text-align: justify;">
                {intro_text}
            </div>
        """

    # Declarações numeradas
    declarations_html = ""
    if declarations:
        items_html = ""
        for decl in declarations:
            items_html += f"""
                <div style="font-family: {Fonts.FAMILY}; font-size: 16px; color: {Colors.PRIMARY}; margin-bottom: {Spacing.MD}; text-align: justify;">
                    {decl}
                </div>
            """
        declarations_html = (
            f'<div style="margin-bottom: {Spacing.MD};">{items_html}</div>'
        )

    # Data e local - texto centralizado simples
    date_location_html = ""
    if date_location_text:
        date_location_html = f"""
            <div style="text-align: center; margin-top: 24px; margin-bottom: 48px;">
                <div style="font-family: {Fonts.FAMILY}; font-size: 16px; color: {Colors.PRIMARY};">
                    {date_location_text}
                </div>
            </div>
        """

    # Linha de assinatura com texto e Nome/CPF abaixo
    signature_html = ""
    if name_cpf_text or signature_text:
        signature_label_html = ""
        if signature_text:
            signature_label_html = f"""
                <div style="font-family: {Fonts.FAMILY}; font-size: 16px; color: {Colors.PRIMARY}; text-align: center; margin-bottom: {Spacing.SM};">
                    {signature_text}
                </div>
            """

        # Linha horizontal de assinatura (sem texto)
        signature_line = f"""
            <div style="border-top: 1px solid {Colors.BORDER}; width: 500px; margin: 0 auto; margin-bottom: {Spacing.MD};">
            </div>
        """

        name_line = ""
        if name_cpf_text:
            name_line = f"""
                <div style="font-family: {Fonts.FAMILY}; font-size: 16px; color: {Colors.PRIMARY}; text-align: center;">
                    {name_cpf_text}
                </div>
            """

        signature_html = f"""
            <div style="text-align: center; margin-top: {Spacing.LG};">
                {signature_label_html}
                {signature_line}
                {name_line}
            </div>
        """

    return f"""
        <div style="font-family: {Fonts.FAMILY}; font-size: 16px; color: {Colors.PRIMARY}; margin-top: 16px;">
            {header_html}
            {annex_html}
            {intro_html}
            {declarations_html}
            {date_location_html}
            {signature_html}
        </div>
    """
