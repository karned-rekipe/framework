import tempfile
from pathlib import Path

import pytest
import yaml

from arclith.infrastructure.config import (
    AppConfig,
    DuckDBSettings,
    SoftDeleteSettings,
    load_config,
)


def test_default_config_uses_memory():
    assert AppConfig().adapters.repository == "memory"


def test_default_retention_is_none():
    assert AppConfig().soft_delete.retention_days is None


def _write_yaml(data: dict) -> Path:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
    yaml.dump(data, f)
    f.close()
    return Path(f.name)


def test_load_config_memory():
    path = _write_yaml({"adapters": {"repository": "memory"}})
    config = load_config(path)
    path.unlink()
    assert config.adapters.repository == "memory"


def test_load_empty_file_uses_defaults():
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
    f.write("")
    f.close()
    path = Path(f.name)
    config = load_config(path)
    path.unlink()
    assert config.adapters.repository == "memory"


def test_duckdb_settings_file_path():
    s = DuckDBSettings(path="data/entities.csv")
    assert s.path == "data/entities.csv"


def test_duckdb_settings_directory_path():
    s = DuckDBSettings(path="data/")
    assert s.path == "data/"


def test_duckdb_settings_invalid_extension():
    with pytest.raises(Exception):
        DuckDBSettings(path="data/file.txt")


def test_soft_delete_negative_raises():
    with pytest.raises(Exception):
        SoftDeleteSettings(retention_days=-1)


def test_soft_delete_zero_is_valid():
    s = SoftDeleteSettings(retention_days=0)
    assert s.retention_days == 0


def test_mongodb_uri_optional_at_parse_time():
    # uri can be None at parse time — resolved via secrets at runtime
    config = AppConfig.model_validate({
        "adapters": {
            "repository": "mongodb",
            "mongodb": {"db_name": "test"},
        }
    })
    assert config.adapters.mongodb is not None
    assert config.adapters.mongodb.uri is None


def test_mongodb_multitenant_no_uri_required():
    config = AppConfig.model_validate({
        "adapters": {
            "repository": "mongodb",
            "multitenant": True,
            "mongodb": {"db_name": "test"},
        }
    })
    assert config.adapters.multitenant is True


def test_duckdb_requires_section():
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        AppConfig.model_validate({"adapters": {"repository": "duckdb"}})


def test_mongodb_requires_section():
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        AppConfig.model_validate({"adapters": {"repository": "mongodb"}})
