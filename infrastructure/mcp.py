import fastmcp

from adapters.input.ingredient_fastmcp import IngredientMCP
from adapters.output.console_logger import ConsoleLogger
from adapters.output.in_memory_ingredient_repository import InMemoryIngredientRepository
from domain.services.ingredient_service import IngredientService


def create_mcp() -> fastmcp.FastMCP:
    mcp = fastmcp.FastMCP("Rekipe - Ingredients")

    logger = ConsoleLogger()
    ingredient_repository = InMemoryIngredientRepository()
    ingredient_service = IngredientService(ingredient_repository, logger)
    IngredientMCP(ingredient_service, logger, mcp)

    return mcp

