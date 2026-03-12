from typing import Generic, TypeVar

from domain.models.entity import Entity
from domain.ports.repository import Repository

T = TypeVar("T", bound=Entity)


class FindAllUseCase(Generic[T]):
    def __init__(self, repository: Repository[T]) -> None:
        self._repository = repository

    def execute(self) -> list[T]:
        return self._repository.find_all()

