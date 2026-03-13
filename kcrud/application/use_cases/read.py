from typing import Generic, Optional, TypeVar
from uuid6 import UUID

from kcrud.domain.models.entity import Entity
from kcrud.domain.ports.logger import Logger
from kcrud.domain.ports.repository import Repository

T = TypeVar("T", bound=Entity)


class ReadUseCase(Generic[T]):
    def __init__(self, repository: Repository[T], logger: Logger) -> None:
        self._repository = repository
        self._logger = logger

    async def execute(self, uuid: UUID) -> Optional[T]:
        self._logger.info("🔍 Reading entity", uuid=str(uuid))
        result = await self._repository.read(uuid)
        if result is None or result.is_deleted:
            self._logger.warning("⚠️ Entity not found", uuid=str(uuid))
            return None
        self._logger.info("✅ Entity found", type=type(result).__name__, uuid=str(uuid))
        return result

