from domain.models.ingredient import Ingredient
from domain.ports.ingredient_repository import IngredientRepository
from domain.ports.logger import Logger
from domain.services.base_service import BaseService


class IngredientService(BaseService[Ingredient]):
    def __init__(self, repository: IngredientRepository, logger: Logger) -> None:
        super().__init__(repository, logger)
        self._repository = repository
        self._logger = logger

    def find_by_name(self, name: str) -> list[Ingredient]:
        self._logger.info("🔍 Finding ingredients by name", name=name)
        result = self._repository.find_by_name(name)
        self._logger.info("✅ Ingredients found", name=name, count=len(result))
        return result
