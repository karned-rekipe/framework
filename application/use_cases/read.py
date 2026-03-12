from typing import Generic, Optional, TypeVar
from uuid6 import UUID

from domain.models.entity import Entity
from domain.ports.repository import Repository

T = TypeVar("T", bound=Entity)


class ReadUseCase(Generic[T]):
    def __init__(self, repository: Repository[T]) -> None:
        self._repository = repository

    def execute(self, uuid: UUID) -> Optional[T]:
        return self._repository.read(uuid)

