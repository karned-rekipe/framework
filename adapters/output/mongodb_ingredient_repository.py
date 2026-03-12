from motor.motor_asyncio import AsyncIOMotorCollection

from domain.models.ingredient import Ingredient
from domain.ports.ingredient_repository import IngredientRepository
from adapters.output.mongodb_repository import MongoDBRepository


class MongoDBIngredientRepository(MongoDBRepository[Ingredient], IngredientRepository):
    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        super().__init__(collection, Ingredient)

    async def find_by_name(self, name: str) -> list[Ingredient]:
        return [
            self._from_doc(doc)
            async for doc in self._collection.find({"name": {"$regex": name, "$options": "i"}})
        ]

