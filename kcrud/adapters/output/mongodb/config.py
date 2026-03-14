from dataclasses import dataclass


@dataclass(frozen = True)
class MongoDBConfig:
    db_name: str
    collection_name: str
    uri: str | None = None
