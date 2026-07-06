from ..logger import register_log_notification_handler
from .teams import TeamsLogHandler

register_log_notification_handler("teams", TeamsLogHandler)


def init_integrations():
    pass


def close_integrations():
    pass
