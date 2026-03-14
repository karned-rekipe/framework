from dataclasses import replace
from typing import Generic, Optional, TypeVar
from uuid6 import UUID, uuid7

from kcrud.domain.models.entity import Entity
from kcrud.domain.ports.repository import Repository

T = TypeVar("T", bound = Entity)


class InMemoryRepository(Repository[T], Generic[T]):
    def __init__(self) -> None:
        self._store: dict[UUID, T] = {}

    async def create(self, entity: T) -> T:
        self._store[entity.uuid] = entity
        return entity

    async def read(self, uuid: UUID) -> Optional[T]:
        return self._store.get(uuid)

    async def update(self, entity: T) -> T:
        self._store[entity.uuid] = entity
        return entity

    async def delete(self, uuid: UUID) -> None:
        self._store.pop(uuid, None)

    async def find_all(self) -> list[T]:
        return [e for e in self._store.values() if not e.is_deleted]

    async def find_deleted(self) -> list[T]:
        return [e for e in self._store.values() if e.is_deleted]

    async def duplicate(self, uuid: UUID) -> T:
        entity = self._store.get(uuid)
        if entity is None or entity.is_deleted:
            raise KeyError(f"Entity with uuid {uuid} not found")
        clone = replace(entity, uuid = uuid7())
        self._store[clone.uuid] = clone
        return clone
