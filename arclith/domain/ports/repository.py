from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

from uuid6 import UUID

from arclith.domain.models.entity import Entity

T = TypeVar("T", bound=Entity)


class Repository(ABC, Generic[T]):
    @abstractmethod
    async def create(self, entity: T) -> T:
        pass  # pragma: no cover

    @abstractmethod
    async def read(self, uuid: UUID) -> Optional[T]:
        pass  # pragma: no cover

    @abstractmethod
    async def update(self, entity: T) -> T:
        pass  # pragma: no cover

    @abstractmethod
    async def delete(self, uuid: UUID) -> None:
        pass  # pragma: no cover

    @abstractmethod
    async def find_all(self) -> list[T]:
        pass  # pragma: no cover

    @abstractmethod
    async def find_deleted(self) -> list[T]:
        pass  # pragma: no cover

    @abstractmethod
    async def duplicate(self, uuid: UUID) -> T:
        pass  # pragma: no cover
