from dataclasses import asdict, fields, replace
from datetime import datetime
from typing import Any, Generic, Optional, TypeVar
from uuid6 import UUID, uuid7
from motor.motor_asyncio import AsyncIOMotorClient

from kcrud.adapters.output.mongodb.config import MongoDBConfig
from kcrud.domain.models.entity import Entity
from kcrud.domain.ports.repository import Repository

T = TypeVar("T", bound = Entity)


class MongoDBRepository(Repository[T], Generic[T]):
    def __init__(self, config: MongoDBConfig, entity_class: type[T]) -> None:
        self._config = config
        self._entity_class = entity_class
        client = AsyncIOMotorClient(config.uri)
        self._collection = client[config.db_name][config.collection_name]

    def _to_doc(self, entity: T) -> dict[str, Any]:
        doc = asdict(entity)
        doc["_id"] = str(doc.pop("uuid"))
        for key, value in doc.items():
            if isinstance(value, datetime):
                doc[key] = value.isoformat()
        return doc

    def _from_doc(self, doc: dict[str, Any]) -> T:
        doc = dict(doc)
        doc["uuid"] = UUID(doc.pop("_id"))
        entity_fields = {f.name for f in fields(self._entity_class)}
        for key in list(doc.keys()):
            if key not in entity_fields:
                doc.pop(key)
            elif isinstance(doc[key], str):
                try:
                    doc[key] = datetime.fromisoformat(doc[key])
                except ValueError:
                    pass
        return self._entity_class(**doc)

    async def create(self, entity: T) -> T:
        await self._collection.insert_one(self._to_doc(entity))
        return entity

    async def read(self, uuid: UUID) -> Optional[T]:
        doc = await self._collection.find_one({"_id": str(uuid)})
        return self._from_doc(doc) if doc else None

    async def update(self, entity: T) -> T:
        await self._collection.replace_one({"_id": str(entity.uuid)}, self._to_doc(entity))
        return entity

    async def delete(self, uuid: UUID) -> None:
        await self._collection.delete_one({"_id": str(uuid)})

    async def find_all(self) -> list[T]:
        return [self._from_doc(doc) async for doc in self._collection.find({"deleted_at": None})]

    async def find_deleted(self) -> list[T]:
        return [self._from_doc(doc) async for doc in self._collection.find({"deleted_at": {"$ne": None}})]

    async def duplicate(self, uuid: UUID) -> T:
        doc = await self._collection.find_one({"_id": str(uuid), "deleted_at": None})
        if doc is None:
            raise KeyError(f"Entity with uuid {uuid} not found")
        clone = self._from_doc({**doc})
        clone = replace(clone, uuid = uuid7())
        await self._collection.insert_one(self._to_doc(clone))
        return clone
