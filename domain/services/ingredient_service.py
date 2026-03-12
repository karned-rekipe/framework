from domain.models.ingredient import Ingredient
from domain.ports.ingredient_repository import IngredientRepository
from domain.services.base_service import BaseService


class IngredientService(BaseService[Ingredient]):
    def __init__(self, repository: IngredientRepository) -> None:
        super().__init__(repository)
        self._repository = repository

    def find_by_name(self, name: str) -> list[Ingredient]:
        return self._repository.find_by_name(name)

