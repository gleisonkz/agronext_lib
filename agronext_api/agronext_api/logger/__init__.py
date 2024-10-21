import logging
import logging.config
import logging.handlers
import pathlib

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "non_error_filter": {"()": "agronext_api.logger.filters.NonErrorFilter"},
    },
    "formatters": {
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
    "handlers": {
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
        # "console": {
        #     "class": "logging.handlers.RotatingFileHandler",
        #     "level": "DEBUG",
        #     "formatter": "json",
        #     "filename": "/tmp/logs/backend.log.jsonl",
        #     "maxBytes": 10000000,
        #     "backupCount": 3,
        # },
        "cloud_run": {
            "class": "logging.StreamHandler",
            "level": "WARNING",
            "formatter": "json",
            "stream": "ext://sys.stdout",
        },
        "queue_handler": {
            "class": "logging.handlers.QueueHandler",
            "respect_handler_level": True,
            "handlers": ["cloud_run", "stdout"],  # ["stderr", "stdout", "cloud_run"],
        },
    },
    "loggers": {
        "root": {"level": "DEBUG", "handlers": ["queue_handler"]},
    },
}


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def _create_logs_dir() -> None:
    logs_path = "/tmp/logs"
    pathlib.Path(logs_path).mkdir(parents=True, exist_ok=True)


def init_logger(log_level: str) -> None:
    LOGGING_CONFIG["loggers"]["root"]["level"] = log_level
    logging.config.dictConfig(LOGGING_CONFIG)
    logging.info(f"Logger initialized with level: {log_level}")

    queue_handler = logging.getHandlerByName("queue_handler")
    queue_handler.listener.start()


def close_logger() -> None:
    queue_handler = logging.getHandlerByName("queue_handler")
    queue_handler.listener.stop()
    logging.shutdown()
