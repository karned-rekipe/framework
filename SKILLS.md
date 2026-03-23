# SKILLS.md — framework (`arclith`)

## SK-F01 — Ajouter un adaptateur de persistance

**Contexte :** implémenter un nouveau backend de stockage (ex. Redis, PostgreSQL).

### Étapes

1. **Créer** `arclith/adapters/output/<backend>/repository.py`
    - Sous-classer `Repository[T]` (ou `InMemoryRepository` pour partir d'une base)
    - Implémenter les 7 méthodes abstraites : `create`, `read`, `update`, `delete`, `find_all`, `find_deleted`,
      `duplicate`

2. **Brancher** dans `arclith/infrastructure/repository_factory.py`
   ```python
   case "<backend>":
       from arclith.adapters.output.<backend>.repository import <Backend>Repository
       return <Backend>Repository(...)
   ```

3. **Config** — ajouter la nouvelle valeur dans le `Literal` de `AdaptersSettings.repository` (
   `infrastructure/config.py`)

4. **Optional-dep** — ajouter le groupe dans `pyproject.toml` :
   ```toml
   [project.optional-dependencies]
   <backend> = ["<package>==x.y.z"]
   ```

5. **Tests** — `tests/units/adapters/output/<backend>/test_repository.py` : coverage ≥ 90 %

### Validation

```bash
make coverage
```

---

## SK-F02 — Étendre `Entity` avec un nouveau champ commun

**Contexte :** ajouter un champ partagé par toutes les entités (ex. `tenant_id`).

### Étapes

1. `arclith/domain/models/entity.py` — ajouter le champ avec valeur par défaut
2. Vérifier que tous les adaptateurs existants (MongoDB, DuckDB, memory) gèrent le champ
3. Mettre à jour les tests unitaires de `Entity`
4. Bump de version mineure dans `pyproject.toml`

### Validation

```bash
make test
make coverage
```

---

## SK-F03 — Ajouter une méthode de requête au port `Repository`

**Contexte :** ajouter une méthode de recherche (ex. `find_by_name`) au contrat de base.

### Étapes

1. `arclith/domain/ports/repository.py` — déclarer la méthode abstraite
2. Implémenter dans **chacun** des adaptateurs : `InMemoryRepository`, `MongoDBRepository`, `DuckDBRepository`
3. Ajouter dans `BaseService` si elle doit être exposée comme use case standard
4. Mettre à jour les tests de chaque adaptateur

> ⚠️ Un ajout au port de base est un **breaking change** : tous les sous-classeurs existants doivent l'implémenter.
> Préférer un port spécialisé dans le repo consommateur si la méthode n'est pas universelle.

### Validation

```bash
make test
make typecheck
```

---

## SK-F04 — Configurer le mode multitenant

**Contexte :** permettre l'isolation par tenant via `ContextVar`.

### Étapes côté framework (déjà implémenté)

- `arclith/adapters/context.py` : `set_tenant_uri(uri)` / `get_tenant_uri()`
- `arclith/adapters/input/fastmcp/dependencies.py` : `make_inject_tenant_uri(config)`

### Étapes côté implémenteur

1. `config.yaml` : `adapters.multitenant: true`
2. Dans l'adapter d'entrée, avant chaque appel :
   ```python
   from arclith.adapters.context import set_tenant_uri
   set_tenant_uri(uri_resolved_from_request)
   ```
3. `MongoDBRepository` appelle `get_tenant_uri()` automatiquement si `multitenant=true`.

### Validation

- Test unitaire avec deux URIs distinctes : vérifier que les collections MongoDB ciblées sont différentes.

