from adapters.output.console_logger import ConsoleLogger
from adapters.output.in_memory_ingredient_repository import InMemoryIngredientRepository
from domain.ports.ingredient_repository import IngredientRepository
from domain.ports.logger import Logger
from domain.services.ingredient_service import IngredientService
from infrastructure.config import AppConfig, load_config


def _build_logger(config: AppConfig) -> Logger:
    return ConsoleLogger()


def _build_repository(config: AppConfig) -> IngredientRepository:
    match config.adapters.repository:
        case "mongodb":
            from adapters.output.mongodb_config import MongoDBConfig
            from adapters.output.mongodb_ingredient_repository import MongoDBIngredientRepository
            if config.adapters.mongodb is None:
                raise ValueError("repository=mongodb mais aucune section [adapters.mongodb] dans config.yaml")
            mongo = config.adapters.mongodb
            return MongoDBIngredientRepository(MongoDBConfig(uri=mongo.uri, db_name=mongo.db_name, collection_name=mongo.collection_name))
        case _:
            return InMemoryIngredientRepository()


def build_ingredient_service() -> tuple[IngredientService, Logger]:
    config = load_config()
    logger = _build_logger(config)
    repository = _build_repository(config)
    return IngredientService(repository, logger), logger


