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
    multitenant: bool = False


class DuckDBSettings(BaseModel):
    path: str
    multitenant: bool = False

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
    mongodb: MongoDBSettings | None = None
    duckdb: DuckDBSettings | None = None

    @property
    def multitenant(self) -> bool:
        """True si au moins un adaptateur a multitenant activé.

        Permet le mode mixte : ex. MongoDB multitenant + MariaDB single-tenant.
        """
        return (
            (self.mongodb.multitenant if self.mongodb else False)
            or (self.duckdb.multitenant if self.duckdb else False)
        )

    @model_validator(mode="after")
    def validate_repository_config(self) -> "AdaptersSettings":
        if self.repository == "mongodb":
            if self.mongodb is None:
                raise ValueError("repository=mongodb mais aucune section [adapters.mongodb] dans config.yaml")
        elif self.repository == "duckdb" and self.duckdb is None:
            raise ValueError("repository=duckdb mais aucune section [adapters.duckdb] dans config.yaml")
        return self


class ApiSettings(BaseModel):
    host: str = "0.0.0.0"  # nosec B104
    port: int = 8000
    reload: bool = True


class McpSettings(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8001


class ProbeSettings(BaseModel):
    host: str = "0.0.0.0"  # nosec B104
    port: int = 9000
    enabled: bool = True


class KeycloakSettings(BaseModel):
    url: str
    realm: str
    audience: str | None = None


class TenantSettings(BaseModel):
    vault_addr: str = "http://127.0.0.1:8200"
    vault_mount: str = "kv"
    vault_path_prefix: str
    tenant_claim: str = "sub"


class LicenseSettings(BaseModel):
    role: str = "rekipe:licensed"


class CacheSettings(BaseModel):
    backend: Literal["memory", "redis"] = "memory"
    redis_url: str = "redis://127.0.0.1:6379"
    jwks_ttl: int = 3600    # secondes
    tenant_uri_ttl: int = 300  # secondes


class AppSettings(BaseModel):
    name: str = "arclith-service"
    version: str = "0.0.0"
    description: str = "API service built with arclith framework"


class AppConfig(BaseModel):
    app: AppSettings = AppSettings()
    adapters: AdaptersSettings = AdaptersSettings()
    soft_delete: SoftDeleteSettings = SoftDeleteSettings()
    api: ApiSettings = ApiSettings()
    mcp: McpSettings = McpSettings()
    probe: ProbeSettings = ProbeSettings()
    keycloak: KeycloakSettings | None = None
    tenant: TenantSettings | None = None
    license: LicenseSettings | None = None
    cache: CacheSettings = CacheSettings()


def load_config(path: Path) -> AppConfig:
    with open(path) as f:
        data = yaml.safe_load(f)
    data = data or {}

    from arclith.infrastructure.secret_factory import build_secret_resolver
    from arclith.infrastructure.secret_loader import resolve_dict_secrets
    from contextlib import suppress

    resolver = build_secret_resolver(data, path.parent)
    if resolver:
        with suppress(Exception):
            data = resolve_dict_secrets(data, resolver)

    return AppConfig.model_validate(data)

_DUCKDB_SUPPORTED_EXTENSIONS = {".csv", ".parquet", ".json", ".arrow"}


class MongoDBSettings(BaseModel):
    uri: str | None = None
    db_name: str
    collection_name: str | None = None
    multitenant: bool = False


class DuckDBSettings(BaseModel):
    path: str
    multitenant: bool = False

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
    mongodb: MongoDBSettings | None = None
    duckdb: DuckDBSettings | None = None

    @property
    def multitenant(self) -> bool:
        match self.repository:
            case "mongodb":
                return self.mongodb.multitenant if self.mongodb else False
            case "duckdb":
                return self.duckdb.multitenant if self.duckdb else False
            case _:
                return False

    @model_validator(mode = "after")
    def validate_repository_config(self) -> "AdaptersSettings":
        if self.repository == "mongodb":
            if self.mongodb is None:
                raise ValueError("repository=mongodb mais aucune section [adapters.mongodb] dans config.yaml")
        elif self.repository == "duckdb" and self.duckdb is None:
            raise ValueError("repository=duckdb mais aucune section [adapters.duckdb] dans config.yaml")
        return self


class ApiSettings(BaseModel):
    host: str = "0.0.0.0"  # nosec B104
    port: int = 8000
    reload: bool = True


class McpSettings(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8001


class ProbeSettings(BaseModel):
    host: str = "0.0.0.0"  # nosec B104
    port: int = 9000
    enabled: bool = True


class AppSettings(BaseModel):
    name: str = "arclith-service"
    version: str = "0.0.0"
    description: str = "API service built with arclith framework"


class AppConfig(BaseModel):
    app: AppSettings = AppSettings()
    adapters: AdaptersSettings = AdaptersSettings()
    soft_delete: SoftDeleteSettings = SoftDeleteSettings()
    api: ApiSettings = ApiSettings()
    mcp: McpSettings = McpSettings()
    probe: ProbeSettings = ProbeSettings()


def load_config(path: Path) -> AppConfig:
    with open(path) as f:
        data = yaml.safe_load(f)
    data = data or {}

    from arclith.infrastructure.secret_factory import build_secret_resolver
    from arclith.infrastructure.secret_loader import resolve_dict_secrets
    from contextlib import suppress

    resolver = build_secret_resolver(data, path.parent)
    if resolver:
        with suppress(Exception):
            data = resolve_dict_secrets(data, resolver)

    return AppConfig.model_validate(data)
