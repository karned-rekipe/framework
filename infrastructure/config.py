from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel

_CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"


class MongoDBSettings(BaseModel):
    uri: str
    db_name: str
    collection_name: str


class AdaptersSettings(BaseModel):
    logger: Literal["console"] = "console"
    repository: Literal["memory", "mongodb"] = "memory"
    mongodb: MongoDBSettings | None = None


class AppConfig(BaseModel):
    adapters: AdaptersSettings = AdaptersSettings()


def load_config(path: Path = _CONFIG_PATH) -> AppConfig:
    with open(path) as f:
        data = yaml.safe_load(f)
    return AppConfig.model_validate(data or {})

