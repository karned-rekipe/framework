from dataclasses import asdict, fields, replace
from datetime import datetime
from pathlib import Path
from typing import Any, Generic, Optional, TypeVar
from uuid6 import UUID, uuid7

import duckdb

from arclith.domain.models.entity import Entity

T = TypeVar("T", bound = Entity)

_SUPPORTED_EXTENSIONS = {".csv", ".parquet", ".json", ".arrow"}


def _validate_file(path: Path) -> None:
    ext = path.suffix.lower()
    if ext not in _SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Format '{ext}' non supporté. "
            f"Formats acceptés : {', '.join(sorted(_SUPPORTED_EXTENSIONS))}"
        )
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {path}")


def _read_file(con: duckdb.DuckDBPyConnection, path: Path) -> duckdb.DuckDBPyRelation:
    ext = path.suffix.lower()
    p = str(path)
    match ext:
        case ".csv":
            return con.read_csv(p)
        case ".parquet":
            return con.read_parquet(p)
        case ".json":
            return con.read_json(p)
        case ".arrow":
            return con.from_arrow(p)
        case _:
            raise ValueError(f"Format non supporté : {ext}")


def _write_file(con: duckdb.DuckDBPyConnection, table: str, path: Path) -> None:
    ext = path.suffix.lower()
    p = str(path)
    match ext:
        case ".csv":
            con.execute(f"COPY {table} TO '{p}' (FORMAT CSV, HEADER)")
        case ".parquet":
            con.execute(f"COPY {table} TO '{p}' (FORMAT PARQUET)")
        case ".json":
            con.execute(f"COPY {table} TO '{p}' (FORMAT JSON)")
        case _:
            raise ValueError(f"Écriture non supportée pour le format : {ext}")


class DuckDBRepository(Repository[T], Generic[T]):
    def __init__(self, path: str | Path, entity_class: type[T]) -> None:
        self._path = Path(path)
        self._entity_class = entity_class
        self._table = entity_class.__name__.lower()
        _validate_file(self._path)
        self._con = duckdb.connect()
        self._load()

    def _load(self) -> None:
        rel = _read_file(self._con, self._path)
        self._con.execute(f"CREATE OR REPLACE TABLE {self._table} AS SELECT * FROM rel")

    def _persist(self) -> None:
        _write_file(self._con, self._table, self._path)

    def _row_to_entity(self, row: dict[str, Any]) -> T:
        entity_fields = {f.name for f in fields(self._entity_class)}
        cleaned = {k: v for k, v in row.items() if k in entity_fields}
        for k, v in cleaned.items():
            if isinstance(v, str):
                try:
                    cleaned[k] = datetime.fromisoformat(v)
                except ValueError:
                    pass
        if "uuid" in cleaned and isinstance(cleaned["uuid"], str):
            cleaned["uuid"] = UUID(cleaned["uuid"])
        return self._entity_class(**cleaned)

    def _entity_to_row(self, entity: T) -> dict[str, Any]:
        row = asdict(entity)
        row["uuid"] = str(row["uuid"])
        for k, v in row.items():
            if isinstance(v, datetime):
                row[k] = v.isoformat()
        return row

    def _fetch(self, sql: str, params: list | None = None) -> list[dict[str, Any]]:
        cur = self._con.execute(sql, params or [])
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]

    async def create(self, entity: T) -> T:
        row = self._entity_to_row(entity)
        cols = ", ".join(row.keys())
        placeholders = ", ".join("?" for _ in row)
        self._con.execute(f"INSERT INTO {self._table} ({cols}) VALUES ({placeholders})", list(row.values()))
        self._persist()
        return entity

    async def read(self, uuid: UUID) -> Optional[T]:
        rows = self._fetch(f"SELECT * FROM {self._table} WHERE uuid = ?", [str(uuid)])
        return self._row_to_entity(rows[0]) if rows else None

    async def update(self, entity: T) -> T:
        row = self._entity_to_row(entity)
        sets = ", ".join(f"{k} = ?" for k in row if k != "uuid")
        values = [v for k, v in row.items() if k != "uuid"] + [str(entity.uuid)]
        self._con.execute(f"UPDATE {self._table} SET {sets} WHERE uuid = ?", values)
        self._persist()
        return entity

    async def delete(self, uuid: UUID) -> None:
        self._con.execute(f"DELETE FROM {self._table} WHERE uuid = ?", [str(uuid)])
        self._persist()

    async def find_all(self) -> list[T]:
        rows = self._fetch(f"SELECT * FROM {self._table} WHERE deleted_at IS NULL")
        return [self._row_to_entity(r) for r in rows]

    async def find_deleted(self) -> list[T]:
        rows = self._fetch(f"SELECT * FROM {self._table} WHERE deleted_at IS NOT NULL")
        return [self._row_to_entity(r) for r in rows]

    async def duplicate(self, uuid: UUID) -> T:
        entity = await self.read(uuid)
        if entity is None or entity.is_deleted:
            raise KeyError(f"Entity with uuid {uuid} not found")
        clone = replace(entity, uuid = uuid7())
        return await self.create(clone)
