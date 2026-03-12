from typing import Generic, Optional, TypeVar
from uuid6 import UUID

from domain.models.entity import Entity
from domain.ports.repository import Repository
from application.use_cases import (
    CreateUseCase,
    ReadUseCase,
    UpdateUseCase,
    DeleteUseCase,
    FindAllUseCase,
    DuplicateUseCase,
)

T = TypeVar("T", bound=Entity)


class BaseService(Generic[T]):
    def __init__(self, repository: Repository[T]) -> None:
        self._create = CreateUseCase(repository)
        self._read = ReadUseCase(repository)
        self._update = UpdateUseCase(repository)
        self._delete = DeleteUseCase(repository)
        self._find_all = FindAllUseCase(repository)
        self._duplicate = DuplicateUseCase(repository)

    def create(self, entity: T) -> T:
        return self._create.execute(entity)

    def read(self, uuid: UUID) -> Optional[T]:
        return self._read.execute(uuid)

    def update(self, entity: T) -> T:
        return self._update.execute(entity)

    def delete(self, uuid: UUID) -> None:
        self._delete.execute(uuid)

    def find_all(self) -> list[T]:
        return self._find_all.execute()

    def duplicate(self, uuid: UUID) -> T:
        return self._duplicate.execute(uuid)

