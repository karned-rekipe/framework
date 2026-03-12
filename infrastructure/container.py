from adapters.output.console_logger import ConsoleLogger
from adapters.output.in_memory_ingredient_repository import InMemoryIngredientRepository
from domain.ports.logger import Logger
from domain.services.ingredient_service import IngredientService


def build_logger() -> Logger:
    return ConsoleLogger()


def build_ingredient_service(logger: Logger | None = None) -> tuple[IngredientService, Logger]:
    logger = logger or build_logger()
    repository = InMemoryIngredientRepository()
    return IngredientService(repository, logger), logger


