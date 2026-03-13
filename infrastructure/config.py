from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, field_validator

_CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"


class MongoDBSettings(BaseModel):
    uri: str
    db_name: str
    collection_name: str


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
    repository: Literal["memory", "mongodb"] = "memory"
    mongodb: MongoDBSettings | None = None


class AppConfig(BaseModel):
    adapters: AdaptersSettings = AdaptersSettings()
    soft_delete: SoftDeleteSettings = SoftDeleteSettings()


def load_config(path: Path = _CONFIG_PATH) -> AppConfig:
    with open(path) as f:
        data = yaml.safe_load(f)
    return AppConfig.model_validate(data or {})

