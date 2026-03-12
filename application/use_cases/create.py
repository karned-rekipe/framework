from typing import Generic, TypeVar

from domain.models.entity import Entity
from domain.ports.logger import Logger
from domain.ports.repository import Repository

T = TypeVar("T", bound=Entity)


class CreateUseCase(Generic[T]):
    def __init__(self, repository: Repository[T], logger: Logger) -> None:
        self._repository = repository
        self._logger = logger

    def execute(self, entity: T) -> T:
        self._logger.info("➕ Creating entity", type=type(entity).__name__, uuid=str(entity.uuid))
        result = self._repository.create(entity)
        self._logger.info("✅ Entity created", type=type(result).__name__, uuid=str(result.uuid))
        return result
