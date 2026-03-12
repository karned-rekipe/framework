from fastapi import FastAPI

from adapters.input.ingredient_fastapi import IngredientRouter
from adapters.output.console_logger import ConsoleLogger
from adapters.output.in_memory_ingredient_repository import InMemoryIngredientRepository
from domain.services.ingredient_service import IngredientService


def create_api() -> FastAPI:
    api = FastAPI()

    logger = ConsoleLogger()
    ingredient_repository = InMemoryIngredientRepository()
    ingredient_service = IngredientService(ingredient_repository, logger)
    ingredient_router = IngredientRouter(ingredient_service, logger)

    api.include_router(ingredient_router.router)

    return api

