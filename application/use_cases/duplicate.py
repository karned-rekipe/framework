from typing import Generic, TypeVar
from uuid6 import UUID

from domain.models.entity import Entity
from domain.ports.repository import Repository

T = TypeVar("T", bound=Entity)


class DuplicateUseCase(Generic[T]):
    def __init__(self, repository: Repository[T]) -> None:
        self._repository = repository

    def execute(self, uuid: UUID) -> T:
        return self._repository.duplicate(uuid)

