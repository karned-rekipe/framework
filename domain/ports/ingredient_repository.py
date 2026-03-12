from abc import abstractmethod

from domain.models.ingredient import Ingredient
from domain.ports.repository import Repository


class IngredientRepository(Repository[Ingredient]):
    @abstractmethod
    async def find_by_name(self, name: str) -> list[Ingredient]:
        pass
