from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, field_validator, model_validator

_DUCKDB_SUPPORTED_EXTENSIONS = {".csv", ".parquet", ".json", ".arrow"}


class MongoDBSettings(BaseModel):
    uri: str | None = None
    db_name: str
    collection_name: str | None = None


class DuckDBSettings(BaseModel):
    path: str

    @field_validator("path")
    @classmethod
    def must_be_supported_format(cls, v: str) -> str:
        p = Path(v)
        if p.is_dir() or v.endswith("/"):
            return v
        ext = p.suffix.lower()
        if ext not in _DUCKDB_SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Format '{ext}' non supporté par DuckDB. "
                f"Formats acceptés : {', '.join(sorted(_DUCKDB_SUPPORTED_EXTENSIONS))}"
            )
        return v


class SoftDeleteSettings(BaseModel):
    retention_days: float | None = None

    @field_validator("retention_days")
    @classmethod
    def must_be_positive(cls, v: float | None) -> float | None:
        if v is not None and v < 0:
            raise ValueError("retention_days doit être >= 0")
        return v


class AdaptersSettings(BaseModel):
    logger: Literal["console"] = "console"
    repository: Literal["memory", "mongodb", "duckdb"] = "memory"
    multitenant: bool = False
    mongodb: MongoDBSettings | None = None
    duckdb: DuckDBSettings | None = None

    @model_validator(mode = "after")
    def validate_repository_config(self) -> "AdaptersSettings":
        if self.repository == "mongodb":
            if self.mongodb is None:
                raise ValueError("repository=mongodb mais aucune section [adapters.mongodb] dans config.yaml")
            if not self.multitenant and not self.mongodb.uri:
                raise ValueError("adapters.mongodb.uri est requis quand multitenant est false")
        elif self.repository == "duckdb" and self.duckdb is None:
            raise ValueError("repository=duckdb mais aucune section [adapters.duckdb] dans config.yaml")
        return self


class ApiSettings(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True


class McpSettings(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8001


class AppConfig(BaseModel):
    adapters: AdaptersSettings = AdaptersSettings()
    soft_delete: SoftDeleteSettings = SoftDeleteSettings()
    api: ApiSettings = ApiSettings()
    mcp: McpSettings = McpSettings()


def load_config(path: Path) -> AppConfig:
    with open(path) as f:
        data = yaml.safe_load(f)
    return AppConfig.model_validate(data or {})
