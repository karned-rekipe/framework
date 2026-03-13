from typing import Generic, TypeVar
from uuid6 import UUID

from kcrud.domain.models.entity import Entity
from kcrud.domain.ports.logger import Logger
from kcrud.domain.ports.repository import Repository

T = TypeVar("T", bound=Entity)


class DuplicateUseCase(Generic[T]):
    def __init__(self, repository: Repository[T], logger: Logger) -> None:
        self._repository = repository
        self._logger = logger

    async def execute(self, uuid: UUID) -> T:
        self._logger.info("📋 Duplicating entity", uuid=str(uuid))
        result = await self._repository.duplicate(uuid)
        self._logger.info("✅ Entity duplicated", original_uuid=str(uuid), new_uuid=str(result.uuid))
        return result

