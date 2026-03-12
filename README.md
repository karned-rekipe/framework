# framework

## Architecture

**domain/models/**
Entités et objets valeur du domaine métier (ex: Recipe, Ingredient) — aucune dépendance extérieure

**domain/ports/**
Interfaces abstraites (ABC) définissant les contrats entre le domaine et le monde extérieur

**domain/services/**
Services métier purs qui orchestrent la logique domaine sans toucher l'infrastructure

**application/use_cases/**
Cas d'usage applicatifs — orchestrent les ports et services pour répondre à une intention utilisateur

**adapters/input/**
Adaptateurs entrants — traduisent une requête externe (CLI, HTTP, événement…) en appel de cas d'usage

**adapters/output/**
Adaptateurs sortants — implémentent les ports de sortie (base de données, API tierce, fichier…)

**infrastructure/**
Câblage global — instanciation et injection des dépendances, configuration, point d'entrée de l'app

---

## Lancement

### Prérequis

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 1. API REST (FastAPI)

Expose un CRUD HTTP sur les ingrédients.

```bash
python main_api.py
```

- Swagger UI : [http://localhost:8000/docs](http://localhost:8000/docs)
- Base URL : `http://localhost:8000/ingredient/v1/`

### 2. Serveur MCP stdio

Utilisé par les clients MCP locaux (Claude Desktop, Cursor…). Le client lance le process lui-même.

```bash
python main_mcp.py
```

Configuration `mcp.json` :

```json
{
  "mcpServers": {
    "rekipe-ingredients": {
      "command": "/chemin/vers/.venv/bin/python",
      "args": ["/chemin/vers/framework/main_mcp.py"]
    }
  }
}
```

### 3. Serveur MCP SSE

Expose les outils MCP via HTTP SSE. Le serveur doit tourner avant que le client s'y connecte.

```bash
python main_mcp_sse.py
```

- SSE endpoint : `http://localhost:8000/sse`

Configuration `mcp.json` :

```json
{
  "mcpServers": {
    "rekipe-ingredients-sse": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

> **Note** : les serveurs MCP (stdio et SSE) partagent la même instance `create_mcp()` définie dans `infrastructure/mcp.py`. Ajouter un nouveau transport ne nécessite aucune modification du domaine.

