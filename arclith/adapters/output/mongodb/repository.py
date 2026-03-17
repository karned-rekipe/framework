from datetime import datetime
from typing import Any, Generic, Optional, TypeVar

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from uuid6 import UUID, uuid7

from arclith.adapters.context import get_tenant_uri
from arclith.adapters.output.mongodb.config import MongoDBConfig
from arclith.domain.models.entity import Entity
from arclith.domain.ports.logger import Logger
from arclith.domain.ports.repository import Repository

T = TypeVar("T", bound = Entity)


class _MongoCollection:
    # Cache de clients par URI pour réutiliser le pool de connexions Motor
    _clients: dict[str, AsyncIOMotorClient] = {}

    def __init__(self, config: MongoDBConfig, logger: Logger) -> None:
        self._config = config
        self._logger = logger
        self._client: AsyncIOMotorClient | None = None

    async def __aenter__(self) -> AsyncIOMotorCollection:
        effective_uri = get_tenant_uri() or self._config.uri
        if not effective_uri:
            raise ValueError("Aucune URI MongoDB : configurez uri ou activez le mode multitenant")

        # Réutilise un client existant pour cette URI si possible, sinon en crée un nouveau.
        if effective_uri in self._clients:
            self._client = self._clients[effective_uri]
        else:
            self._client = AsyncIOMotorClient(effective_uri)
            self._clients[effective_uri] = self._client
            self._logger.debug(
                "🔌 MongoDB client created",
                db=self._config.db_name,
                collection=self._config.collection_name,
            )

        self._logger.debug(
            "🔌 MongoDB collection acquired",
            db=self._config.db_name,
            collection=self._config.collection_name,
        )
        return self._client[self._config.db_name][self._config.collection_name]  # type: ignore[return-value]

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        # Ne ferme plus le client ici pour conserver le pool Motor.
        self._logger.debug(
            "🔌 MongoDB collection released",
            db=self._config.db_name,
            collection=self._config.collection_name,
        )


class MongoDBRepository(Repository[T], Generic[T]):
    def __init__(self, config: MongoDBConfig, entity_class: type[T], logger: Logger) -> None:
        self._config = config
        self._entity_class = entity_class
        self._logger = logger

    def _collection(self) -> _MongoCollection:
        return _MongoCollection(self._config, self._logger)

    def _to_doc(self, entity: T) -> dict[str, Any]:
        doc = entity.model_dump()
        doc["_id"] = str(doc.pop("uuid"))
        for key, value in doc.items():
            if isinstance(value, datetime):
                doc[key] = value.isoformat()
        return doc

    def _from_doc(self, doc: dict[str, Any]) -> T:
        doc = dict(doc)
        doc["uuid"] = UUID(doc.pop("_id"))
        entity_fields = set(self._entity_class.model_fields.keys())
        datetime_fields = {"created_at", "updated_at", "deleted_at"}
        for key in list(doc.keys()):
            if key not in entity_fields:
                doc.pop(key)
            elif isinstance(doc[key], str) and key in datetime_fields:
                try:
                    doc[key] = datetime.fromisoformat(doc[key])
                except ValueError:
                    self._logger.warning(
                        f"Failed to parse field '{key}' as datetime from value {doc[key]!r}; leaving as string."
                    )
        return self._entity_class(**doc)

    async def create(self, entity: T) -> T:
        async with self._collection() as col:
            await col.insert_one(self._to_doc(entity))
        return entity

    async def read(self, uuid: UUID) -> Optional[T]:
        async with self._collection() as col:
            doc = await col.find_one({"_id": str(uuid)})
        return self._from_doc(doc) if doc else None

    async def update(self, entity: T) -> T:
        async with self._collection() as col:
            await col.replace_one({"_id": str(entity.uuid)}, self._to_doc(entity))
        return entity

    async def delete(self, uuid: UUID) -> None:
        async with self._collection() as col:
            await col.delete_one({"_id": str(uuid)})

    async def find_all(self) -> list[T]:
        async with self._collection() as col:
            return [self._from_doc(doc) async for doc in col.find({"deleted_at": None})]

    async def find_deleted(self) -> list[T]:
        async with self._collection() as col:
            return [self._from_doc(doc) async for doc in col.find({"deleted_at": {"$ne": None}})]

    async def duplicate(self, uuid: UUID) -> T:
        async with self._collection() as col:
            doc = await col.find_one({"_id": str(uuid), "deleted_at": None})
            if doc is None:
                raise KeyError(f"Entity with uuid {uuid} not found")
            clone = self._from_doc({**doc}).model_copy(update={"uuid": uuid7()})
            await col.insert_one(self._to_doc(clone))
        return clone
