import asyncio
import logging

import httpx

from ..config.base_settings import BaseSettings, SettingsConfigDict
from ..logger import get_logger

teams_logger = get_logger("teams")
ERRORS_LOGGER_NAME = "errors"


class TeamsSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    teams_webhook_url: str = ""


teams_settings = TeamsSettings()


def build_payload(text: str) -> dict:
    return {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4",
        "body": [{"type": "TextBlock", "text": text, "wrap": True}],
    }


def format_teams_message(record: logging.LogRecord) -> str:
    if isinstance(record.msg, dict):
        details = record.msg
        status_code = details.get("status_code", 500)
        method = details.get("method", "?")
        url = details.get("url", "?")
        detail = (
            details.get("detail")
            or details.get("exception_message")
            or details.get("error")
            or str(details)
        )
        return f"Erro {status_code} — {method} {url}\n{detail}"
    return record.getMessage()


def _post_teams(text: str) -> bool:
    url = teams_settings.teams_webhook_url
    if not url:
        return False
    try:
        with httpx.Client(timeout=15) as client:
            response = client.post(
                url,
                json=build_payload(text),
                headers={"Content-Type": "application/json"},
            )
        teams_logger.info("[teams] POST status=%s", response.status_code)
        return response.status_code in (200, 202)
    except Exception:
        teams_logger.exception("[teams] failed to send notification")
        return False


async def send_teams(text: str) -> bool:
    return await asyncio.to_thread(_post_teams, text)


class ErrorsLoggerFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.name == ERRORS_LOGGER_NAME


class TeamsLogHandler(logging.Handler):
    """Envia alertas ao Teams a partir do QueueListener de logs de erro."""

    def __init__(self) -> None:
        super().__init__(level=logging.ERROR)
        self.addFilter(ErrorsLoggerFilter())

    def emit(self, record: logging.LogRecord) -> None:
        try:
            _post_teams(format_teams_message(record))
        except Exception:
            self.handleError(record)
