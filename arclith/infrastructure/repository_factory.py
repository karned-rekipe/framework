
from __future__ import annotations
from typing import TypeVar
from arclith.domain.models.entity import Entity
from arclith.domain.ports.logger import Logger
from arclith.domain.ports.repository import Repository
from arclith.infrastructure.config import AppConfig
T = TypeVar("T", bound=Entity)
def build_repository(config: AppConfig, entity_class: type[T], logger: Logger) -> Repository[T]:
    match config.adapters.repository:
        case "mongodb":
            from arclith.adapters.output.mongodb.config import MongoDBConfig
            from arclith.adapters.output.mongodb.repository import MongoDBRepository
            mongo = config.adapters.mongodb
            return MongoDBRepository(
                MongoDBConfig(uri=mongo.uri, db_name=mongo.db_name, collection_name=mongo.collection_name),
                entity_class, logger,
            )
        case "duckdb":
            from arclith.adapters.output.duckdb.repository import DuckDBRepository
            return DuckDBRepository(config.adapters.duckdb.path, entity_class)
        case _:
            from arclith.adapters.output.memory.repository import InMemoryRepository
            return InMemoryRepository()
