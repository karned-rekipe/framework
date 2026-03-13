from dataclasses import replace
from datetime import datetime, timezone
from typing import Generic, TypeVar

from domain.models.entity import Entity
from domain.ports.logger import Logger
from domain.ports.repository import Repository

T = TypeVar("T", bound=Entity)


class CreateUseCase(Generic[T]):
    def __init__(self, repository: Repository[T], logger: Logger) -> None:
        self._repository = repository
        self._logger = logger

    async def execute(self, entity: T) -> T:
        now = datetime.now(timezone.utc)
        entity = replace(entity, created_at=now, updated_at=now)
        self._logger.info("➕ Creating entity", type=type(entity).__name__, uuid=str(entity.uuid))
        result = await self._repository.create(entity)
        self._logger.info("✅ Entity created", type=type(result).__name__, uuid=str(result.uuid))
        return result
