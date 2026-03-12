from abc import ABC, abstractmethod
from enum import Enum
from typing import Any


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class Logger(ABC):
    @abstractmethod
    def log(self, level: LogLevel, message: str, **metadata: Any) -> None:
        pass

    def debug(self, message: str, **metadata: Any) -> None:
        self.log(LogLevel.DEBUG, message, **metadata)

    def info(self, message: str, **metadata: Any) -> None:
        self.log(LogLevel.INFO, message, **metadata)

    def warning(self, message: str, **metadata: Any) -> None:
        self.log(LogLevel.WARNING, message, **metadata)

    def error(self, message: str, **metadata: Any) -> None:
        self.log(LogLevel.ERROR, message, **metadata)



