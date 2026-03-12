from fastapi import FastAPI

from adapters.input.ingredient_fastapi import IngredientRouter
from infrastructure.container import build_ingredient_service


def create_api() -> FastAPI:
    api = FastAPI()

    ingredient_service, logger = build_ingredient_service()
    ingredient_router = IngredientRouter(ingredient_service, logger)

    api.include_router(ingredient_router.router)

    return api

