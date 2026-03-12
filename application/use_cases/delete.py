from typing import Generic, TypeVar
from uuid6 import UUID

from domain.models.entity import Entity
from domain.ports.logger import Logger
from domain.ports.repository import Repository

T = TypeVar("T", bound=Entity)


class DeleteUseCase(Generic[T]):
    def __init__(self, repository: Repository[T], logger: Logger) -> None:
        self._repository = repository
        self._logger = logger

    async def execute(self, uuid: UUID) -> None:
        self._logger.info("🗑️ Deleting entity", uuid=str(uuid))
        await self._repository.delete(uuid)
        self._logger.info("✅ Entity deleted", uuid=str(uuid))
