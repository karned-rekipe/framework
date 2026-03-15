from __future__ import annotations
import logging
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeVar
from arclith.domain.models.entity import Entity
from arclith.domain.ports.logger import Logger, LogLevel
from arclith.domain.ports.repository import Repository
from arclith.infrastructure.config import AppConfig, load_config
if TYPE_CHECKING:
    import fastmcp
    from fastapi import FastAPI
T = TypeVar("T", bound=Entity)
_UVICORN_LOG_CONFIG: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {},
    "loggers": {
        "uvicorn": {"handlers": [], "propagate": True},
        "uvicorn.access": {"handlers": [], "propagate": True},
        "uvicorn.error": {"handlers": [], "propagate": True},
    },
}
_LEVEL_MAP: dict[str, LogLevel] = {
    "DEBUG": LogLevel.DEBUG,
    "INFO": LogLevel.INFO,
    "WARNING": LogLevel.WARNING,
    "ERROR": LogLevel.ERROR,
    "CRITICAL": LogLevel.CRITICAL,
}
class _UvicornLogInterceptHandler(logging.Handler):
    def __init__(self, logger: Logger) -> None:
        super().__init__()
        self._logger = logger
    def emit(self, record: logging.LogRecord) -> None:
        self._logger.log(_LEVEL_MAP.get(record.levelname, LogLevel.INFO), record.getMessage())
class Arclith:
    def __init__(self, config_path: str | Path) -> None:
        self.config: AppConfig = load_config(Path(config_path))
    @cached_property
    def logger(self) -> Logger:
        from arclith.adapters.output.console.logger import ConsoleLogger
        return ConsoleLogger()
    def repository(self, entity_class: type[T]) -> "Repository[T]":
        from arclith.infrastructure.repository_factory import build_repository
        return build_repository(self.config, entity_class, self.logger)
    def fastapi(self, **kwargs: Any) -> "FastAPI":
        from fastapi import FastAPI
        return FastAPI(**kwargs)
    def fastmcp(self, name: str, **kwargs: Any) -> "fastmcp.FastMCP":
        import fastmcp
        return fastmcp.FastMCP(name, **kwargs)
    def run_api(self, app: "FastAPI | str") -> None:
        import uvicorn
        self._setup_uvicorn_logging()
        uvicorn.run(
            app,  # type: ignore[arg-type]
            host=self.config.api.host,
            port=self.config.api.port,
            reload=self.config.api.reload if isinstance(app, str) else False,
            log_config=_UVICORN_LOG_CONFIG,
        )
    def run_mcp_stdio(self, mcp: "fastmcp.FastMCP") -> None:
        mcp.run(transport="stdio")
    def run_mcp_sse(self, mcp: "fastmcp.FastMCP") -> None:
        mcp.run(transport="sse", host=self.config.mcp.host, port=self.config.mcp.port)
    def _setup_uvicorn_logging(self) -> None:
        handler = _UvicornLogInterceptHandler(self.logger)
        logging.root.handlers = [handler]
        logging.root.setLevel(logging.DEBUG)
        for name in ("uvicorn", "uvicorn.access", "uvicorn.error", "watchfiles"):
            log = logging.getLogger(name)
            log.handlers = [handler]
            log.propagate = False
