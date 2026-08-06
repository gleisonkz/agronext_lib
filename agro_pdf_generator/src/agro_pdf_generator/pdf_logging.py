import logging


NOISY_PDF_BACKEND_LOGGERS = (
    # "weasyprint",
    # "weasyprint.progress",
    "fontTools",
    "fontTools.subset",
)


def disable_noisy_pdf_backend_loggers() -> None:
    for logger_name in NOISY_PDF_BACKEND_LOGGERS:
        logging.getLogger(logger_name).disabled = True