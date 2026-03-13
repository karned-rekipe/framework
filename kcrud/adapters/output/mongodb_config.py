from dataclasses import dataclass


@dataclass(frozen=True)
class MongoDBConfig:
    uri: str
    db_name: str
    collection_name: str

