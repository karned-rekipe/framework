# Architecture

kcrud suit les principes de l'**architecture hexagonale** (Ports & Adapters) combinés à la **Clean Architecture**.

La règle fondamentale : les dépendances ne vont que vers l'intérieur.

```
adapters / infrastructure
        ↓
   application
        ↓
     domain
```

---

## `domain/`

Le cœur métier. Aucune dépendance externe, aucun I/O.

### `domain/models/`

Les entités métier. Elles héritent de `Entity` (uuid, timestamps, soft-delete).

```python
@dataclass
class Ingredient(Entity):
    name: str = ""
    unit: str | None = None
```

### `domain/ports/`

Les interfaces (abstractions) que le domaine expose vers l'extérieur.

- `Repository[T]` — contrat de persistance (create, read, update, delete, find_all…)
- `Logger` — contrat de logging

> C'est ici que tu définis aussi tes ports spécifiques (ex: `IngredientRepository` avec `find_by_name`).

---

## `application/`

Orchestration. Coordonne les ports du domaine pour réaliser des cas d'usage concrets.

### `application/use_cases/`

Un fichier = un cas d'usage = une seule responsabilité.

Fournis par le framework : `CreateUseCase`, `ReadUseCase`, `UpdateUseCase`, `DeleteUseCase`, `FindAllUseCase`,
`DuplicateUseCase`, `PurgeUseCase`.

> Ajoute ici tes use cases spécifiques (ex: `FindByNameUseCase`).

### `application/services/`

Façade qui regroupe les use cases d'une entité sous une API cohérente.
Les adapters input (FastAPI, MCP…) ne parlent qu'aux services.

`BaseService` est fourni par le framework. Étends-le pour ajouter tes méthodes métier.

```python
class IngredientService(BaseService[Ingredient]):
    async def find_by_name(self, name: str) -> list[Ingredient]:
        ...
```

---

## `adapters/`

Les implémentations concrètes des ports. Ils dépendent du domaine, jamais l'inverse.

### `adapters/input/`

Points d'entrée de l'application (ce qui déclenche des actions).

- Routeurs FastAPI
- Outils MCP (FastMCP)

### `adapters/input/schemas/`

Les schémas Pydantic de validation des données entrantes/sortantes.
Ils ne doivent pas fuiter dans le domaine.

`BaseSchema` est fourni par le framework comme base commune.

### `adapters/output/`

Implémentations des ports de persistance et de logging.

Fournis par le framework :

- `InMemoryRepository` — dev / tests
- `DuckDBRepository` — fichier local (CSV, Parquet…)
- `MongoDBRepository` — production
- `ConsoleLogger` — logging structuré en console

> Étends ces classes pour brancher ton entité sur un repository concret.

---

## `infrastructure/`

Configuration et assemblage. Ne contient pas de logique métier.

- `config.py` / `AppConfig` — lecture du `config.yaml` (quel repository, quelle DB…)
- `container.py` *(dans ton app)* — instancie et injecte les dépendances (DI manuel)
- `api.py` / `mcp.py` *(dans ton app)* — monte les adapters sur le serveur

---

## Résumé

| Dossier           | Rôle                          | Dépend de                 |
|-------------------|-------------------------------|---------------------------|
| `domain/`         | Logique métier pure           | Rien                      |
| `application/`    | Orchestration des cas d'usage | `domain/`                 |
| `adapters/`       | Implémentations concrètes     | `domain/`, `application/` |
| `infrastructure/` | Config & assemblage           | Tout                      |

