import sys
import yaml
import json
import queue
import logging
from logging import DEBUG, INFO  # noqa: F401
from logging.config import dictConfig
from pathlib import Path
from typing import Optional, Union, Dict
from logging.handlers import QueueHandler, QueueListener

# Replace this with your real JSONFormatter
from .formatters import JSONFormatter

# ── 1) Filters ────────────────────────────────────────────────────────────────


class MaxLevelFilter(logging.Filter):
    """Allow only records at or below a given level."""

    def __init__(self, max_level: int):
        super().__init__()
        self.max_level = max_level

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno <= self.max_level


# ── 2) Default formatters ─────────────────────────────────────────────────────

_SIMPLE_FMT = "%(levelname)s:\t[%(name)s] - %(asctime)s - %(message)s"
_DETAILED_FMT = "[%(levelname)s|%(module)s|L%(lineno)d] %(asctime)s: %(message)s"
_ISO_DATEFMT = "%Y-%m-%dT%H:%M:%S%z"
_HUMAN_DATEFMT = "%Y-%m-%d %H:%M:%S"


# ── 3) Globals ────────────────────────────────────────────────────────────────

_log_queue = queue.Queue(-1)
_listener: Optional[QueueListener] = None


# ── 4) Initialization ─────────────────────────────────────────────────────────


def init_logger(
    level: int = INFO,
    override: Optional[Union[str, Dict]] = None,
) -> None:
    """
    - level: root logging level (e.g. "DEBUG", "INFO")
    - override: either a path to a YAML/JSON file, or a raw dict following
      the same schema as DEFAULT_LOGGING_CONFIG, to completely replace defaults.
    """
    global _listener

    # 1) Don’t double‐start
    if (
        _listener is not None
        and getattr(_listener, "thread", None)
        and _listener.thread.is_alive()
    ):
        logging.getLogger(__name__).warning("Logger already initialized; skipping.")
        return

    # 2) If override is given, delegate to dictConfig (but strip any illegal keys)
    if override:
        if isinstance(override, str):
            text = Path(override).read_text()
            raw_cfg = (
                yaml.safe_load(text)
                if override.lower().endswith((".yml", ".yaml"))
                else json.loads(text)
            )
        else:
            raw_cfg = override.copy()
        # Remove any 'name' keys so StreamHandler() calls don’t blow up:
        for cfg in raw_cfg.get("handlers", {}).values():
            cfg.pop("name", None)

        dictConfig(raw_cfg)
        # Now find the handlers we need by inspecting their formatter/type:
        root = logging.getLogger()
        stdout_h = next(
            h
            for h in root.handlers
            if isinstance(h, logging.StreamHandler)
            and getattr(h.formatter, "fmt", "").startswith("%(levelname)s:\t")
        )
        stderr_h = next(
            h
            for h in root.handlers
            if isinstance(h, logging.StreamHandler) and h.stream is sys.stderr
        )
        cloud_h = next(
            h
            for h in root.handlers
            if isinstance(h, logging.StreamHandler)
            and isinstance(h.formatter, JSONFormatter)
        )
    else:
        # 3) Programmatic default setup
        root = logging.getLogger()
        root.setLevel(level)

        # clean out any existing handlers on root
        for h in list(root.handlers):
            root.removeHandler(h)

        # build the three workers
        stdout_h = logging.StreamHandler(sys.stdout)
        stdout_h.setLevel(logging.DEBUG)
        stdout_h.addFilter(MaxLevelFilter(logging.INFO))
        stdout_h.setFormatter(logging.Formatter(_SIMPLE_FMT, datefmt=_HUMAN_DATEFMT))

        stderr_h = logging.StreamHandler(sys.stderr)
        stderr_h.setLevel(logging.WARNING)
        stderr_h.setFormatter(logging.Formatter(_DETAILED_FMT, datefmt=_ISO_DATEFMT))

        cloud_h = logging.StreamHandler(sys.stdout)
        cloud_h.setLevel(logging.WARNING)
        cloud_h.setFormatter(JSONFormatter())

        # attach the queue
        queue_h = QueueHandler(_log_queue)
        queue_h.setLevel(level)
        root.addHandler(queue_h)

    # 4) Start the listener
    handlers = (stdout_h, stderr_h, cloud_h)
    _listener = QueueListener(_log_queue, *handlers, respect_handler_level=True)
    _listener.start()

    logging.getLogger(__name__).info(f"Logging initialized at level={level!r}")


def close_logger() -> None:
    """Stop the background listener and shut down logging cleanly."""
    global _listener
    if _listener:
        _listener.stop()
        _listener = None
    logging.shutdown()


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
