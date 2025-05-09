import logging


class MaxLevelFilter(logging.Filter):
    """
    Allow only log records at or below the configured maximum level.
    """

    def __init__(self, name: str = "", max_level: int | str = logging.INFO):
        super().__init__(name)
        # Accept level names (e.g. "INFO") or ints (20)
        if isinstance(max_level, str):
            # map string names to numeric levels
            max_level = logging._nameToLevel.get(max_level, logging.INFO)
        self.max_level = max_level

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno <= self.max_level
