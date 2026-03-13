from typing import Generic, Optional, TypeVar
from uuid6 import UUID

from domain.models.entity import Entity
from domain.ports.logger import Logger
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
    def __init__(self, repository: Repository[T], logger: Logger, retention_days: float | None = None) -> None:
        self._create = CreateUseCase(repository, logger)
        self._read = ReadUseCase(repository, logger)
        self._update = UpdateUseCase(repository, logger)
        self._delete = DeleteUseCase(repository, logger, retention_days)
        self._find_all = FindAllUseCase(repository, logger)
        self._duplicate = DuplicateUseCase(repository, logger)

    async def create(self, entity: T) -> T:
        return await self._create.execute(entity)

    async def read(self, uuid: UUID) -> Optional[T]:
        return await self._read.execute(uuid)

    async def update(self, entity: T) -> T:
        return await self._update.execute(entity)

    async def delete(self, uuid: UUID, deleted_by: str | None = None) -> None:
        await self._delete.execute(uuid, deleted_by)

    async def find_all(self) -> list[T]:
        return await self._find_all.execute()

    async def duplicate(self, uuid: UUID) -> T:
        return await self._duplicate.execute(uuid)
