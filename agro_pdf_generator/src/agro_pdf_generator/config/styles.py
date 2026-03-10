class Colors:
    PRIMARY = "#1F2937"
    ACCENT = "#0D9488"
    WHITE = "#FFFFFF"
    BORDER = "#1F2937"


class Fonts:
    FAMILY = "Inter, Arial, sans-serif"
    SIZE_TINY = "10px"
    SIZE_SMALL = "12px"
    SIZE_NORMAL = "14px"
    SIZE_MEDIUM = "14px"
    SIZE_LARGE = "16px"
    WEIGHT_NORMAL = "400"
    WEIGHT_SEMIBOLD = "600"


class Spacing:
    XS = "4px"
    SM = "2px"
    MD = "8px"
    LG = "16px"
    XL = "16px"
    XXL = "24px"
    NEG_MD = "-8px"
    NEG_LG = "-16px"


class LineHeight:
    TIGHT = "16px"
    NORMAL = "20px"
    MEDIUM = "20px"
    LOOSE = "24px"
    RELAXED = "28px"


class Layout:
    # Custom size 1192x1755px (~150 DPI)
    PAGE_SIZE = "1192px 1755px"
    PAGE_WIDTH = "1192px"
    PAGE_HEIGHT = "1755px"
    PAGE_PADDING = "24px"
    LOGO_WIDTH = "126px"
    LOGO_HEIGHT = "50px"
    LOGO_HEADER_HEIGHT = "94px"
    LOGO_HEADER_PADDING = "22px"
    BORDER_RADIUS = "8px"
    BORDER_RADIUS_SMALL = "4px"
    CHECKBOX_SIZE = "16px"


class Pagination:
    # 1755 - 48 (padding) - 94 (logo header) = 1613px usable
    MAX_PAGE_HEIGHT = 1613
    SECTION_HEADER_HEIGHT = 40


class Styles:
    FONT_BASE = f"font-family: {Fonts.FAMILY}; color: {Colors.PRIMARY};"

    LABEL = (
        f"font-family: {Fonts.FAMILY}; "
        f"font-size: {Fonts.SIZE_MEDIUM}; "
        f"font-weight: {Fonts.WEIGHT_SEMIBOLD}; "
        f"line-height: {LineHeight.NORMAL}; "
        f"color: {Colors.PRIMARY};"
    )

    VALUE = (
        f"font-family: {Fonts.FAMILY}; "
        f"font-size: {Fonts.SIZE_MEDIUM}; "
        f"font-weight: {Fonts.WEIGHT_NORMAL}; "
        f"line-height: {LineHeight.NORMAL}; "
        f"color: {Colors.PRIMARY};"
    )

    TABLE_HEADER = (
        f"font-family: {Fonts.FAMILY}; "
        f"font-size: {Fonts.SIZE_NORMAL}; "
        f"font-weight: {Fonts.WEIGHT_SEMIBOLD}; "
        f"line-height: {LineHeight.MEDIUM}; "
        f"color: {Colors.PRIMARY};"
    )

    TABLE_CELL = (
        f"font-family: {Fonts.FAMILY}; "
        f"font-size: {Fonts.SIZE_NORMAL}; "
        f"font-weight: {Fonts.WEIGHT_NORMAL}; "
        f"line-height: {LineHeight.TIGHT}; "
        f"color: {Colors.PRIMARY};"
    )

    # Small variant (12px) for dense tables
    TABLE_HEADER_SMALL = (
        f"font-family: {Fonts.FAMILY}; "
        f"font-size: {Fonts.SIZE_SMALL}; "
        f"font-weight: {Fonts.WEIGHT_SEMIBOLD}; "
        f"line-height: {LineHeight.TIGHT}; "
        f"color: {Colors.PRIMARY};"
    )

    TABLE_CELL_SMALL = (
        f"font-family: {Fonts.FAMILY}; "
        f"font-size: {Fonts.SIZE_SMALL}; "
        f"font-weight: {Fonts.WEIGHT_NORMAL}; "
        f"line-height: {Fonts.SIZE_SMALL}; "
        f"color: {Colors.PRIMARY};"
    )

    SIGNATURE_TEXT = (
        f"font-family: {Fonts.FAMILY}; "
        f"font-weight: {Fonts.WEIGHT_NORMAL}; "
        f"font-size: {Fonts.SIZE_MEDIUM}; "
        f"line-height: {LineHeight.NORMAL}; "
        f"color: {Colors.PRIMARY};"
    )

    DISCLAIMER = (
        f"font-family: {Fonts.FAMILY}; "
        f"font-weight: {Fonts.WEIGHT_NORMAL}; "
        f"font-size: {Fonts.SIZE_SMALL}; "
        f"line-height: {LineHeight.NORMAL}; "
        f"color: {Colors.PRIMARY};"
    )

    HTML_BLOCK_TEXT = (
        f"font-family: {Fonts.FAMILY}; "
        f"font-weight: {Fonts.WEIGHT_NORMAL}; "
        f"font-size: {Fonts.SIZE_SMALL}; "
        f"line-height: {LineHeight.LOOSE}; "
        f"color: {Colors.PRIMARY};"
    )

    BORDERED_CONTAINER = (
        f"border: 1px solid {Colors.BORDER}; "
        f"border-radius: {Layout.BORDER_RADIUS}; "
        "overflow: hidden;"
    )

    CHECKBOX_CHECKED = (
        f"width: {Layout.CHECKBOX_SIZE}; "
        f"height: {Layout.CHECKBOX_SIZE}; "
        f"min-width: {Layout.CHECKBOX_SIZE}; "
        f"background: {Colors.PRIMARY}; "
        f"border: 1px solid {Colors.ACCENT}; "
        f"border-radius: {Layout.BORDER_RADIUS_SMALL}; "
        "box-sizing: border-box; "
        "display: flex; "
        "align-items: center; "
        "justify-content: center;"
    )

    CHECKBOX_UNCHECKED = (
        f"width: {Layout.CHECKBOX_SIZE}; "
        f"height: {Layout.CHECKBOX_SIZE}; "
        f"min-width: {Layout.CHECKBOX_SIZE}; "
        f"background: {Colors.WHITE}; "
        f"border: 1px solid {Colors.PRIMARY}; "
        f"border-radius: {Layout.BORDER_RADIUS_SMALL};"
    )

    INFO_TABLE = (
        f"border: 1px solid {Colors.BORDER}; "
        f"border-radius: {Layout.BORDER_RADIUS}; "
        "overflow: hidden; "
        f"margin-bottom: {Spacing.LG};"
    )

    INFO_ROW = "display: flex;"

    INFO_CELL = (
        f"padding: {Spacing.SM} {Spacing.MD}; display: flex; flex-direction: column;"
    )
