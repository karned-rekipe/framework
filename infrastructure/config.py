from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, field_validator

_CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"

_DUCKDB_SUPPORTED_EXTENSIONS = {".csv", ".parquet", ".json", ".arrow"}


class MongoDBSettings(BaseModel):
    uri: str
    db_name: str
    collection_name: str


class DuckDBSettings(BaseModel):
    path: str

    @field_validator("path")
    @classmethod
    def must_be_supported_format(cls, v: str) -> str:
        ext = Path(v).suffix.lower()
        if ext not in _DUCKDB_SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Format '{ext}' non supporté par DuckDB. "
                f"Formats acceptés : {', '.join(sorted(_DUCKDB_SUPPORTED_EXTENSIONS))}"
            )
        return v


class SoftDeleteSettings(BaseModel):
    retention_days: float | None = None  # None = infini, 0 = suppression immédiate

    @field_validator("retention_days")
    @classmethod
    def must_be_positive(cls, v: float | None) -> float | None:
        if v is not None and v < 0:
            raise ValueError("retention_days doit être >= 0")
        return v


class AdaptersSettings(BaseModel):
    logger: Literal["console"] = "console"
    repository: Literal["memory", "mongodb", "duckdb"] = "memory"
    mongodb: MongoDBSettings | None = None
    duckdb: DuckDBSettings | None = None


class ApiSettings(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True


class AppConfig(BaseModel):
    adapters: AdaptersSettings = AdaptersSettings()
    soft_delete: SoftDeleteSettings = SoftDeleteSettings()
    api: ApiSettings = ApiSettings()


def load_config(path: Path = _CONFIG_PATH) -> AppConfig:
    with open(path) as f:
        data = yaml.safe_load(f)
    return AppConfig.model_validate(data or {})

