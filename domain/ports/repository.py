from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar
from uuid6 import UUID

from domain.models.entity import Entity

T = TypeVar("T", bound=Entity)


class Repository(ABC, Generic[T]):
    @abstractmethod
    def create(self, entity: T) -> T:
        pass

    @abstractmethod
    def read(self, uuid: UUID) -> Optional[T]:
        pass

    @abstractmethod
    def update(self, entity: T) -> T:
        pass

    @abstractmethod
    def delete(self, uuid: UUID) -> None:
        pass

    @abstractmethod
    def find_all(self) -> list[T]:
        pass

    @abstractmethod
    def duplicate(self, uuid: UUID) -> T:
        pass


