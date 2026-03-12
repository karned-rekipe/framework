from uuid import UUID as StdUUID
from uuid6 import UUID

import fastmcp

from adapters.input.schemas.ingredient_schema import IngredientSchema
from domain.models.ingredient import Ingredient
from domain.ports.logger import Logger
from domain.services.ingredient_service import IngredientService


class IngredientMCP:
    def __init__(self, service: IngredientService, logger: Logger, mcp: fastmcp.FastMCP) -> None:
        self._service = service
        self._logger = logger
        self._mcp = mcp
        self._register_tools()

    @staticmethod
    def _to_uuid6(uuid: StdUUID) -> UUID:
        return UUID(str(uuid))

    def _register_tools(self) -> None:
        service = self._service
        logger = self._logger
        to_uuid6 = self._to_uuid6

        @self._mcp.tool
        def create_ingredient(name: str, unit: str | None = None) -> dict:
            """Create a new ingredient."""
            ingredient = Ingredient(name=name, unit=unit)
            result = service.create(ingredient)
            return IngredientSchema.model_validate(result).model_dump()

        @self._mcp.tool
        def get_ingredient(uuid: str) -> dict | None:
            """Get an ingredient by its UUID."""
            result = service.read(to_uuid6(StdUUID(uuid)))
            if result is None:
                logger.warning("⚠️ Ingredient not found via MCP", uuid=uuid)
                return None
            return IngredientSchema.model_validate(result).model_dump()

        @self._mcp.tool
        def update_ingredient(uuid: str, name: str, unit: str | None = None) -> dict:
            """Update an existing ingredient."""
            ingredient = Ingredient(uuid=to_uuid6(StdUUID(uuid)), name=name, unit=unit)
            result = service.update(ingredient)
            return IngredientSchema.model_validate(result).model_dump()

        @self._mcp.tool
        def delete_ingredient(uuid: str) -> None:
            """Delete an ingredient by its UUID."""
            service.delete(to_uuid6(StdUUID(uuid)))

        @self._mcp.tool
        def list_ingredients() -> list[dict]:
            """List all ingredients."""
            return [IngredientSchema.model_validate(i).model_dump() for i in service.find_all()]

        @self._mcp.tool
        def duplicate_ingredient(uuid: str) -> dict:
            """Duplicate an ingredient, assigning it a new UUID."""
            result = service.duplicate(to_uuid6(StdUUID(uuid)))
            return IngredientSchema.model_validate(result).model_dump()

        @self._mcp.tool
        def find_ingredients_by_name(name: str) -> list[dict]:
            """Find ingredients whose name contains the given string."""
            return [IngredientSchema.model_validate(i).model_dump() for i in service.find_by_name(name)]


