import logging
import uvicorn

from domain.ports.logger import Logger, LogLevel
from infrastructure.api import create_api


class _InterceptHandler(logging.Handler):
    def __init__(self, logger: Logger) -> None:
        super().__init__()
        self._logger = logger

    def emit(self, record: logging.LogRecord) -> None:
        level_map = {
            "DEBUG": LogLevel.DEBUG,
            "INFO": LogLevel.INFO,
            "WARNING": LogLevel.WARNING,
            "ERROR": LogLevel.ERROR,
            "CRITICAL": LogLevel.CRITICAL,
        }
        level = level_map.get(record.levelname, LogLevel.INFO)
        self._logger.log(level, record.getMessage())


def _setup_uvicorn_logging(logger: Logger) -> None:
    handler = _InterceptHandler(logger)
    for name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        log = logging.getLogger(name)
        log.handlers = [handler]
        log.propagate = False


api, logger = create_api()
_setup_uvicorn_logging(logger)

if __name__ == "__main__":
    uvicorn.run("main_api:api", host="0.0.0.0", port=8000, reload=True)


