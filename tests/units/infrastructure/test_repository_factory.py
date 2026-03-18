import pytest

from arclith.adapters.output.memory.repository import InMemoryRepository
from arclith.domain.models.entity import Entity
from arclith.infrastructure.config import AppConfig, AdaptersSettings, MongoDBSettings, DuckDBSettings
from arclith.infrastructure.repository_factory import build_repository


class Item(Entity):
    name: str = "item"


def test_memory_returns_in_memory_repository(logger):
    config = AppConfig(adapters = AdaptersSettings(repository = "memory"))
    repo = build_repository(config, Item, logger)
    assert isinstance(repo, InMemoryRepository)


def test_mongodb_returns_mongodb_repository(logger):
    pytest.importorskip("motor")
    from arclith.adapters.output.mongodb.repository import MongoDBRepository
    config = AppConfig(adapters = AdaptersSettings(
        repository = "mongodb",
        mongodb = MongoDBSettings(uri = "mongodb://localhost:27017", db_name = "test"),
    ))
    repo = build_repository(config, Item, logger)
    assert isinstance(repo, MongoDBRepository)


def test_duckdb_returns_duckdb_repository(logger, tmp_path):
    pytest.importorskip("duckdb")
    from arclith.adapters.output.duckdb.repository import DuckDBRepository
    config = AppConfig(adapters = AdaptersSettings(
        repository = "duckdb",
        duckdb = DuckDBSettings(path = str(tmp_path) + "/"),
    ))
    repo = build_repository(config, Item, logger)
    assert isinstance(repo, DuckDBRepository)
