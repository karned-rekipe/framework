from typing import Generic, TypeVar

from kcrud.domain.models.entity import Entity
from kcrud.domain.ports.logger import Logger
from kcrud.domain.ports.repository import Repository

T = TypeVar("T", bound=Entity)


class FindAllUseCase(Generic[T]):
    def __init__(self, repository: Repository[T], logger: Logger) -> None:
        self._repository = repository
        self._logger = logger

    async def execute(self) -> list[T]:
        self._logger.info("📋 Finding all entities")
        result = [e for e in await self._repository.find_all() if not e.is_deleted]
        self._logger.info("✅ Entities found", count=len(result))
        return result

