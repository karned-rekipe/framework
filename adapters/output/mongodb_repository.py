from dataclasses import asdict, replace
from typing import Any, Generic, Optional, TypeVar
from uuid6 import UUID, uuid7
from motor.motor_asyncio import AsyncIOMotorCollection

from domain.models.entity import Entity
from domain.ports.repository import Repository

T = TypeVar("T", bound=Entity)


class MongoDBRepository(Repository[T], Generic[T]):
    def __init__(self, collection: AsyncIOMotorCollection, entity_class: type[T]) -> None:
        self._collection = collection
        self._entity_class = entity_class

    def _to_doc(self, entity: T) -> dict[str, Any]:
        doc = asdict(entity)
        doc["_id"] = str(doc.pop("uuid"))
        return doc

    def _from_doc(self, doc: dict[str, Any]) -> T:
        doc["uuid"] = UUID(doc.pop("_id"))
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
        return [self._from_doc(doc) async for doc in self._collection.find()]

    async def duplicate(self, uuid: UUID) -> T:
        doc = await self._collection.find_one({"_id": str(uuid)})
        if doc is None:
            raise KeyError(f"Entity with uuid {uuid} not found")
        clone = self._from_doc({**doc})
        clone = replace(clone, uuid=uuid7())
        await self._collection.insert_one(self._to_doc(clone))
        return clone

