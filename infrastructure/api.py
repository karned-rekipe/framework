from fastapi import FastAPI

from adapters.input.ingredient_router import IngredientRouter
from adapters.output.in_memory_ingredient_repository import InMemoryIngredientRepository
from domain.services.ingredient_service import IngredientService


def create_api() -> FastAPI:
    api = FastAPI()

    ingredient_repository = InMemoryIngredientRepository()
    ingredient_service = IngredientService(ingredient_repository)
    ingredient_router = IngredientRouter(ingredient_service)

    api.include_router(ingredient_router.router)

    return api

