from abc import ABC, abstractmethod
from typing import Optional
from uuid6 import UUID

from domain.models import Item


class ItemRepository(ABC):
    @abstractmethod
    def create(self, item: Item) -> Item:
        pass

    @abstractmethod
    def read(self, uuid: UUID) -> Optional[Item]:
        pass

    @abstractmethod
    def update(self, item: Item) -> Item:
        pass

    @abstractmethod
    def delete(self, uuid: UUID) -> None:
        pass

    @abstractmethod
    def duplicate(self, uuid: UUID) -> Item:
        pass

    @abstractmethod
    def find_all(self) -> list[Item]:
        pass

    @abstractmethod
    def find_by_name(self, name: str) -> list[Item]:
        pass

