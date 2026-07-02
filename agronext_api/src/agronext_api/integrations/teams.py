import httpx

from ..config.base_settings import BaseSettings, SettingsConfigDict
from ..logger import get_logger

teams_logger = get_logger("teams")


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


async def send_teams(text: str) -> bool:
    url = teams_settings.teams_webhook_url
    if not url:
        return False
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                url,
                json=build_payload(text),
                headers={"Content-Type": "application/json"},
            )
        teams_logger.info("[teams] POST status=%s", response.status_code)
        return response.status_code in (200, 202)
    except Exception:
        teams_logger.exception("[teams] failed to send notification")
        return False
