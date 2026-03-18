# Changelog

## [0.2.1] — 2026-03-18

### Fixed

- `DuckDBRepository._load` : `rel` est désormais enregistré via `con.register("rel", rel)` avant son utilisation dans la requête SQL — correction d'un bug potentiel de résolution de variable.
- `_UvicornLogInterceptHandler.emit` : utilise `traceback.format_exception(exc)` (signature Python 3.10+) à la place de `format_exception(*record.exc_info)`.
- `repository_factory` : assertions de vérification null ajoutées sur les configurations `mongodb` et `duckdb` avant utilisation.

### Changed

- `domain/ports/repository.py`, `domain/ports/logger.py` : méthodes abstraites annotées `# pragma: no cover`.
- `arclith/__init__.py` : ordonnancement des imports aligné ; `ConsoleLogger` réexporté pour les type checkers.
- `infrastructure/config.py` : `# nosec B104` sur le host par défaut `0.0.0.0`.

---

## [0.2.0] — 2026-03-18

### Breaking changes

- `Entity` migré de `@dataclass` vers `pydantic.BaseModel` (`model_copy`, `model_dump` remplacent `replace`, `asdict`).
- `MongoDBConfig` migré de `@dataclass` vers `pydantic.BaseModel` (frozen). Le champ `collection_name` devient optionnel et se place après `uri`.

### Added

- `Entity.coerce_uuid` : `field_validator` qui coerce `uuid.UUID` (stdlib) et `str` vers `uuid6.UUID` — corrige les erreurs de désérialisation DuckDB.
- `Entity` : `description` et `examples` sur tous les champs pour exposition OpenAPI / MCP.
- `DuckDBRepository` : création automatique du fichier de données au premier démarrage (CSV et JSON).
- `DuckDBRepository` : `path` peut être un répertoire — le nom de fichier est alors dérivé du nom de la classe entité.
- `MongoDBRepository` : `collection_name` dérivé automatiquement de `entity_class.__name__.lower()` si non fourni.
- `pytz` ajouté à l'extra `duckdb` (requis par DuckDB pour les timestamps avec timezone).

### Fixed

- `_UvicornLogInterceptHandler.emit()` : le traceback complet est désormais inclus dans les logs d'erreur ASGI.
- Suppression de `logging.root.handlers = [handler]` qui contaminait tous les loggers Python.
- Suppression du metadata `source` parasite sur les logs uvicorn.

### Changed

- `application/use_cases` (`create`, `update`, `delete`, `duplicate`) : `dataclasses.replace` remplacé par `model_copy`.
- `adapters/output` (memory, mongodb, duckdb) : `asdict`, `fields`, `replace` remplacés par les équivalents Pydantic.
- `MongoDBSettings` / `DuckDBSettings` dans `AppConfig` : `collection_name` optionnel, validator DuckDB accepte les répertoires.

---

## [0.1.0] — initial release

