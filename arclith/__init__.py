from typing import TYPE_CHECKING

from arclith.adapters.input.schemas.base_schema import BaseSchema
from arclith.adapters.output.memory.repository import InMemoryRepository
from arclith.adapters.output.mongodb.config import MongoDBConfig
from arclith.application.services.base_service import BaseService
from arclith.arclith import Arclith
from arclith.domain.models.entity import Entity
from arclith.domain.ports.logger import Logger, LogLevel
from arclith.domain.ports.repository import Repository
from arclith.infrastructure.adapter_registry import AdapterRegistry
from arclith.infrastructure.config import AppConfig, export_config_yaml, load_config_dir, load_config_file

if TYPE_CHECKING:  # pragma: no cover - for static type checkers only
    from arclith.adapters.output.console.logger import ConsoleLogger as _ConsoleLogger, ConsoleLogger  # noqa: F401

__all__ = [
    "Entity",
    "Repository",
    "Logger",
    "LogLevel",
    "BaseService",
    "BaseSchema",
    "ConsoleLogger",
    "InMemoryRepository",
    "MongoDBConfig",
    "AppConfig",
    "load_config_dir",
    "load_config_file",
    "export_config_yaml",
    "AdapterRegistry",
    "Arclith",
]

def __getattr__(name):
    """
    Lazily import objects that may have side effects at import time.

    This prevents side-effectful modules (such as the ConsoleLogger's Loguru
    configuration) from being imported merely by doing ``import arclith``.
    """
    if name == "ConsoleLogger":
        from arclith.adapters.output.console.logger import ConsoleLogger as _ConsoleLoggerRuntime

        globals()["ConsoleLogger"] = _ConsoleLoggerRuntime
        return _ConsoleLoggerRuntime
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
