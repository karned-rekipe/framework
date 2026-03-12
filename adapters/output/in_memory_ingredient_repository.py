from domain.models.ingredient import Ingredient
from domain.ports.ingredient_repository import IngredientRepository
from adapters.output.in_memory_repository import InMemoryRepository


class InMemoryIngredientRepository(InMemoryRepository[Ingredient], IngredientRepository):
    def find_by_name(self, name: str) -> list[Ingredient]:
        return [i for i in self._store.values() if name.lower() in i.name.lower()]

