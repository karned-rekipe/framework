from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar
from uuid6 import UUID

from domain.models.entity import Entity

T = TypeVar("T", bound=Entity)


class Repository(ABC, Generic[T]):
    @abstractmethod
    async def create(self, entity: T) -> T:
        pass

    @abstractmethod
    async def read(self, uuid: UUID) -> Optional[T]:
        pass

    @abstractmethod
    async def update(self, entity: T) -> T:
        pass

    @abstractmethod
    async def delete(self, uuid: UUID) -> None:
        pass

    @abstractmethod
    async def find_all(self) -> list[T]:
        pass

    @abstractmethod
    async def find_deleted(self) -> list[T]:
        pass

    @abstractmethod
    async def duplicate(self, uuid: UUID) -> T:
        pass
