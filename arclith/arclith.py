from __future__ import annotations

import logging
import threading
import traceback
from collections.abc import Awaitable, Callable
from contextlib import AsyncExitStack, asynccontextmanager
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Any, AsyncIterator, TypeVar

from arclith.domain.models.entity import Entity
from arclith.domain.ports.logger import Logger, LogLevel
from arclith.domain.ports.repository import Repository
from arclith.infrastructure.config import AppConfig, load_config

if TYPE_CHECKING:
    import fastmcp as _fastmcp
    from fastapi import FastAPI

T = TypeVar("T", bound=Entity)
_UVICORN_LOG_CONFIG: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {},
    "loggers": {
        "uvicorn": {"handlers": [], "propagate": False},
        "uvicorn.access": {"handlers": [], "propagate": False},
        "uvicorn.error": {"handlers": [], "propagate": False},
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
        message = record.getMessage()
        if record.exc_info:
            exc = record.exc_info[1]
            tb = "".join(traceback.format_exception(exc))
            message = f"{message}\n{tb}"
        self._logger.log(
            _LEVEL_MAP.get(record.levelname, LogLevel.INFO),
            message,
        )
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
        user_lifespan = kwargs.pop("lifespan", None)
        arclith_self = self

        @asynccontextmanager
        async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
            arclith_self._setup_uvicorn_logging()
            if user_lifespan is not None:
                async with AsyncExitStack() as stack:
                    await stack.enter_async_context(user_lifespan(app))
                    yield
            else:
                yield

        app = FastAPI(lifespan=_lifespan, **kwargs)

        if self.config.probe.enabled:
            from arclith.adapters.input.probes.metrics import ApiMetricsCollector
            # add_middleware(cls, **kwargs) → Starlette calls cls(app=inner_app, registry=…)
            app.add_middleware(ApiMetricsCollector, registry=self._metrics_registry)
            # Probe /metrics reads from same registry via a view instance (app=None, collect() only)
            self._probe_server.add_collector(
                ApiMetricsCollector(app=None, registry=self._metrics_registry)  # type: ignore[arg-type]
            )

        return app

    # ── probe helpers ─────────────────────────────────────────────────────────

    def add_readiness_check(self, fn: Callable[[], Awaitable[bool]]) -> None:
        """Register an async readiness check (e.g. DB ping) exposed on /ready."""
        self._probe_server.add_readiness_check(fn)

    def instrument_mcp(self, mcp: "_fastmcp.FastMCP") -> None:
        """Wrap all registered FastMCP tools with McpMetricsCollector (Option B).

        Call AFTER all tools are registered::

            IngredientMCP(service, logger, mcp)
            arclith.instrument_mcp(mcp)
        """
        if not self.config.probe.enabled:
            return
        collector = self._mcp_collector
        try:
            # fastmcp 3.x: tools live in _local_provider._components as FunctionTool objects
            components: dict[str, Any] = mcp._local_provider._components  # type: ignore[attr-defined]
        except AttributeError:
            self.logger.warning("⚠️ instrument_mcp: cannot access FastMCP components (API changed?)")
            return
        count = 0
        for component in components.values():
            fn = getattr(component, "fn", None)
            if fn is None or not callable(fn):
                continue
            component.fn = collector.wrap(component.name, fn)
            count += 1
        self.logger.info("🔬 MCP tools instrumented", count=count)

    def run_with_probes(
        self,
        *runners: Callable[[], None],
        transports: list[str] | None = None,
    ) -> None:
        """Start ProbeServer (background daemon) then run service runner(s).

        - 1 runner  → runs in the main thread (blocking, current behaviour).
        - N runners → each in its own non-daemon thread; main thread joins (MODE=all).

        ``transports`` populates /info → active_transports.
        Note: mcp_stdio is incompatible with MODE=all.
        """
        if not runners:
            return

        if transports:
            self._probe_server.set_active_transports(transports)

        if self.config.probe.enabled:
            self._probe_server.start_in_background()

        if len(runners) == 1:
            runners[0]()
            return

        threads = [
            threading.Thread(target=r, daemon=False, name=f"runner-{i}")
            for i, r in enumerate(runners)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

    # ── runners ───────────────────────────────────────────────────────────────

    def fastmcp(self, name: str, **kwargs: Any) -> "_fastmcp.FastMCP":
        import fastmcp
        return fastmcp.FastMCP(name, **kwargs)

    def run_api(self, app: "FastAPI | str") -> None:
        import uvicorn
        uvicorn.run(
            app,  # type: ignore[arg-type]
            host=self.config.api.host,
            port=self.config.api.port,
            reload=self.config.api.reload if isinstance(app, str) else False,
            log_config=_UVICORN_LOG_CONFIG,
        )

    def run_mcp_stdio(self, mcp: "_fastmcp.FastMCP") -> None:
        mcp.run(transport="stdio")

    def run_mcp_sse(self, mcp: "_fastmcp.FastMCP") -> None:
        mcp.run(transport="sse", host=self.config.mcp.host, port=self.config.mcp.port)

    def run_mcp_http(self, mcp: "_fastmcp.FastMCP") -> None:
        mcp.run(transport="streamable-http", host=self.config.mcp.host, port=self.config.mcp.port)

    # ── private cached helpers ────────────────────────────────────────────────

    @cached_property
    def _metrics_registry(self) -> Any:
        from arclith.adapters.input.probes.metrics import MetricsRegistry
        return MetricsRegistry()

    @cached_property
    def _mcp_collector(self) -> Any:
        from arclith.adapters.input.probes.metrics import McpMetricsCollector
        collector = McpMetricsCollector(self._metrics_registry)
        if self.config.probe.enabled:
            self._probe_server.add_collector(collector)
        return collector

    @cached_property
    def _probe_server(self) -> Any:
        from arclith.adapters.input.probes.server import ProbeServer
        probe = self.config.probe
        return ProbeServer(
            host=probe.host,
            port=probe.port,
            service_name=self.config.app.name,
            service_version=self.config.app.version,
        )

    def _setup_uvicorn_logging(self) -> None:
        handler = _UvicornLogInterceptHandler(self.logger)
        for name in ("uvicorn", "uvicorn.access", "uvicorn.error", "watchfiles"):
            log = logging.getLogger(name)
            log.setLevel(logging.DEBUG)
            log.handlers = [handler]
            log.propagate = False
