from typing import Generic, TypeVar

from domain.models.entity import Entity
from domain.ports.logger import Logger
from domain.ports.repository import Repository

T = TypeVar("T", bound=Entity)


class FindAllUseCase(Generic[T]):
    def __init__(self, repository: Repository[T], logger: Logger) -> None:
        self._repository = repository
        self._logger = logger

    async def execute(self) -> list[T]:
        self._logger.info("📋 Finding all entities")
        result = await self._repository.find_all()
        self._logger.info("✅ Entities found", count=len(result))
        return result
