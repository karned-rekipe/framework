import sys
from typing import Any

from loguru import logger as loguru_logger

from domain.ports.logger import Logger, LogLevel

_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level> | {extra}"

loguru_logger.remove()
loguru_logger.add(sys.stderr, format=_FORMAT)


class ConsoleLogger(Logger):
    def log(self, level: LogLevel, message: str, **metadata: Any) -> None:
        bound = loguru_logger.bind(**metadata) if metadata else loguru_logger
        getattr(bound, level.value.lower())(message)
