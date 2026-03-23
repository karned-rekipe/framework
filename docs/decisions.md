# docs/decisions.md — framework (`arclith`)

## ADR-001 — UUIDv7 comme identifiant d'entité

**Contexte :** Choix de l'algorithme d'ID pour les entités.

**Décision :** UUIDv7 via la bibliothèque `uuid6`.

**Pourquoi pas l'alternative évidente (UUIDv4) :**
UUIDv4 est aléatoire — pas d'ordre temporel, ce qui dégrade les index B-tree (MongoDB, DuckDB) et rend le tri par ID
impossible. UUIDv7 est ordonné par le temps à la milliseconde, combine les avantages d'un ULID et d'un UUID standard.

**Conséquence sur le code :**

- `Entity.uuid` est de type `uuid6.UUID`, pas `uuid.UUID` stdlib.
- Les adaptateurs MongoDB stockent l'UUID en string pour compatibilité.
- `@field_validator("uuid", mode="before")` sur `Entity` coerce automatiquement les strings en `UUID`.

---

## ADR-002 — Pydantic v2 comme système de modèles

**Contexte :** Validation et sérialisation des entités et de la config.

**Décision :** Pydantic v2 (`pydantic==2.x`), `BaseModel` avec `ConfigDict`.

**Pourquoi pas l'alternative évidente (dataclasses stdlib) :**
Les dataclasses n'ont pas de validation automatique des types à l'instanciation, pas de sérialisation JSON intégrée, pas
de `field_validator`. Pydantic v2 offre la validation au runtime et est le standard de l'écosystème FastAPI.

**Conséquence sur le code :**

- `Entity` étend `BaseModel`, pas `dataclass`.
- `model_config = ConfigDict(arbitrary_types_allowed=True)` pour accepter `uuid6.UUID`.
- Les `@field_validator` utilisent `mode="before"` pour la coercion.

---

## ADR-003 — Soft-delete par champ `deleted_at`

**Contexte :** Suppression logique des entités sans perte de données.

**Décision :** Champ `deleted_at: datetime | None` sur `Entity`. Suppression physique différée via `PurgeUseCase` selon
`retention_days`.

**Pourquoi pas l'alternative évidente (champ booléen `is_deleted`) :**
Un booléen ne porte pas d'information temporelle. `deleted_at` permet de calculer le délai de rétention sans champ
supplémentaire et de trier les suppressions par date.

**Conséquence sur le code :**

- `find_all()` filtre automatiquement les entités où `deleted_at is not None`.
- `find_deleted()` retourne uniquement les supprimées.
- `PurgeUseCase` supprime physiquement celles dont `deleted_at + retention_days < now`.
- `retention_days: null` = conservation infinie ; `0` = suppression immédiate (pas de soft-delete).

---

## ADR-004 — Optimistic locking via champ `version`

**Contexte :** Prévenir les écritures concurrentes conflictuelles.

**Décision :** Champ `version: int = 1` incrémenté à chaque `update`.

**Pourquoi pas l'alternative évidente (pessimistic locking / transactions) :**
Les transactions MongoDB ont un surcoût significatif. L'optimistic locking est suffisant pour les volumes cibles et
évite les deadlocks dans un contexte async.

**Conséquence sur le code :**

- Les adaptateurs `update()` doivent incrémenter `version` avant persistance.
- Les clients qui soumettent une version obsolète recevront un conflit (à implémenter dans les use cases si nécessaire).

---

## ADR-005 — DuckDB comme adaptateur fichier plutôt que SQLite

**Contexte :** Persistance légère sans serveur pour le dev et les sandboxes.

**Décision :** DuckDB via `duckdb==1.5.0`, formats supportés : `.csv`, `.parquet`, `.json`, `.arrow`.

**Pourquoi pas l'alternative évidente (SQLite) :**
DuckDB est orienté analytique et supporte nativement Parquet, Arrow et CSV sans ORM. Il est plus adapté à des exports de
données et à la lecture de fichiers plats. SQLite nécessiterait un ORM ou du SQL manuel.

**Conséquence sur le code :**

- `DuckDBSettings.path` valide l'extension : seuls `.csv`, `.parquet`, `.json`, `.arrow` sont acceptés (ou un dossier).
- `DuckDBRepository[T]` reconstruit les entités depuis les colonnes du fichier.
- Pas de migrations : le schéma est inféré depuis le modèle Pydantic.

---

## ADR-006 — FastMCP comme couche MCP plutôt qu'une implémentation manuelle

**Contexte :** Exposer les services via le Model Context Protocol.

**Décision :** `fastmcp>=3.1.0` avec trois transports : stdio, SSE, streamable-HTTP.

**Pourquoi pas l'alternative évidente (implémentation MCP manuelle) :**
FastMCP gère la sérialisation, le routing et les transports. Une implémentation manuelle serait fragile et ne suivrait
pas les évolutions du spec MCP.

**Conséquence sur le code :**

- `Arclith.fastmcp(name)` retourne un `FastMCP` instance.
- Les tools sont enregistrés via `@mcp.tool` (décorateur) à l'intérieur des classes `*MCP`.
- `run_mcp_sse()` et `run_mcp_http()` lisent `config.mcp.host` / `config.mcp.port`.

