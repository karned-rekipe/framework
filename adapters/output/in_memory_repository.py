from dataclasses import replace
from typing import Generic, Optional, TypeVar
from uuid6 import UUID, uuid7

from domain.models.entity import Entity
from domain.ports.repository import Repository

T = TypeVar("T", bound=Entity)


class InMemoryRepository(Repository[T], Generic[T]):
    def __init__(self) -> None:
        self._store: dict[UUID, T] = {}

    def create(self, entity: T) -> T:
        self._store[entity.uuid] = entity
        return entity

    def read(self, uuid: UUID) -> Optional[T]:
        return self._store.get(uuid)

    def update(self, entity: T) -> T:
        self._store[entity.uuid] = entity
        return entity

    def delete(self, uuid: UUID) -> None:
        self._store.pop(uuid, None)

    def find_all(self) -> list[T]:
        return list(self._store.values())

    def duplicate(self, uuid: UUID) -> T:
        entity = self._store.get(uuid)
        if entity is None:
            raise KeyError(f"Entity with uuid {uuid} not found")
        clone = replace(entity, uuid=uuid7())
        self._store[clone.uuid] = clone
        return clone


