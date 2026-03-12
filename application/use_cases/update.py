from typing import Generic, TypeVar

from domain.models.entity import Entity
from domain.ports.logger import Logger
from domain.ports.repository import Repository

T = TypeVar("T", bound=Entity)


class UpdateUseCase(Generic[T]):
    def __init__(self, repository: Repository[T], logger: Logger) -> None:
        self._repository = repository
        self._logger = logger

    def execute(self, entity: T) -> T:
        self._logger.info("✏️ Updating entity", type=type(entity).__name__, uuid=str(entity.uuid))
        result = self._repository.update(entity)
        self._logger.info("✅ Entity updated", type=type(result).__name__, uuid=str(result.uuid))
        return result
