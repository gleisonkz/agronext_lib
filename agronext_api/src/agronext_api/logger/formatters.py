import datetime as dt
import json
import logging
from typing import Any
from pythonjsonlogger.jsonlogger import JsonFormatter  # type: ignore

LOG_RECORD_BUILTIN_ATTRS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
    "taskName",
}


class JSONFormatter(logging.Formatter):
    """
    Output a JSON object with:
      - core fields (message, timestamp, exc_info, stack_info)
      - mapped fields per fmt_keys
      - any extras from record.__dict__
    """

    BUILTIN_ATTRS = LOG_RECORD_BUILTIN_ATTRS  # cache

    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        fmt_keys: dict[str, str] | None = None,
    ):
        super().__init__(fmt=fmt, datefmt=datefmt)
        self.fmt_keys = fmt_keys or {}

    def format(self, record: logging.LogRecord) -> str:
        obj = self._prepare_log_dict(record)
        return json.dumps(obj, default=str)

    def _prepare_log_dict(self, record: logging.LogRecord) -> dict[str, Any]:
        # 1. Base fields
        data: dict[str, Any] = {
            "message": record.getMessage(),
            "timestamp": dt.datetime.fromtimestamp(
                record.created, tz=dt.timezone.utc
            ).isoformat(),
        }
        # 2. Exception/stack
        if record.exc_info:
            data["exc_info"] = self.formatException(record.exc_info)
        if record.stack_info:
            data["stack_info"] = self.formatStack(record.stack_info)

        # 3. Mapped keys
        mapped = {
            out_key: record.__dict__.get(in_key)
            for out_key, in_key in self.fmt_keys.items()
            if in_key in record.__dict__ or in_key in data
        }
        data.update(mapped)

        # 4. Extras
        extras = {
            k: v for k, v in record.__dict__.items() if k not in self.BUILTIN_ATTRS
        }
        data.update(extras)

        return data
