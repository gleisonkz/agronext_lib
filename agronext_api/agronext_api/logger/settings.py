from typing import Dict, List, Optional

from pydantic import ConfigDict, Field

from ..config.base_settings import BaseSettings


class FilterConfig(BaseSettings):
    __config__ = ConfigDict(extra="allow")
    callable: str


class FormatterConfig(BaseSettings):
    format: Optional[str] = None
    datefmt: Optional[str] = None
    fmt_keys: Optional[Dict[str, str]] = None
    callable: Optional[str] = None


class HandlerConfig(BaseSettings):
    class_: str = Field(alias="class")
    level: Optional[str] = None
    formatter: Optional[str] = None
    stream: Optional[str] = None
    filename: Optional[str] = None
    maxBytes: Optional[int] = None
    backupCount: Optional[int] = None
    filters: Optional[List[str]] = None
    handlers: Optional[List[str]] = None
    respect_handler_level: Optional[bool] = None


class LoggerConfig(BaseSettings):
    level: str
    handlers: List[str]


class LoggingConfig(BaseSettings):
    version: int
    disable_existing_loggers: bool
    filters: dict[str, FilterConfig]
    formatters: dict[str, FormatterConfig]
    handlers: dict[str, HandlerConfig]
    loggers: dict[str, LoggerConfig]


# Define the configuration using the Pydantic models
logging_config = LoggingConfig(
    version=1,
    disable_existing_loggers=False,
    filters={
        "non_error_filter": {
            "()": "agronext_api.logger.filters.NonErrorFilter",
        }
    },
    formatters={
        "simple": {
            "format": "%(levelname)s:\t[%(name)s] - %(asctime)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "detailed": {
            "format": "[%(levelname)s|%(module)s|L%(lineno)d] %(asctime)s: %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S%z",
        },
        "json": {
            "()": "agronext_api.logger.formatters.JSONFormatter",
            "fmt_keys": {
                "severity": "levelname",
                "message": "message",
                "timestamp": "timestamp",
                "appplication": "pathname",
                "function": "funcName",
                "line": "lineno",
            },
        },
    },
    handlers={
        "stdout": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "level": "DEBUG",
            "filters": ["non_error_filter"],
            "stream": "ext://sys.stdout",
        },
        "stderr": {
            "class": "logging.StreamHandler",
            "level": "WARNING",
            "formatter": "detailed",
            "stream": "ext://sys.stderr",
        },
        "azure": {
            "class": "logging.StreamHandler",
            "level": "WARNING",
            "formatter": "json",
            "stream": "ext://sys.stdout",
        },
        "queue_handler": {
            "class": "logging.handlers.QueueHandler",
            "respect_handler_level": True,
            "handlers": ["azure", "stdout"],
        },
    },
    loggers={"root": {"level": "DEBUG", "handlers": ["queue_handler"]}},
)
