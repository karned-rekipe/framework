# arclith-cli

`arclith-cli` génère instantanément un projet Python en architecture hexagonale prêt à démarrer, en téléchargeant le template officiel `_sample` depuis GitHub et en remplaçant l'entité de démo `Ingredient` par le nom de votre choix. Tout type de projet peut être scaffoldé — service REST, agent IA, API MCP — avec les ports, le nom de projet et le backend de persistance configurés d'emblée. Une seule commande suffit : `arclith-cli new <Entity> <project-name>`.

## Installation

```bash
uv tool install "git+https://github.com/karned-rekipe/framework.git#subdirectory=cli"
```

## Utilisation

```bash
# Nouveau projet
arclith-cli new Recipe my-recipe-service
arclith-cli new RecipeStep meal-planner --port 8400
arclith-cli new MealPlan meal-plan-service --dir ~/projects --port 8500

# Mise à jour
arclith-cli update
```

## Options

| Option | Défaut | Description |
|--------|--------|-------------|
| `--port` / `-p` | `8000` | Port REST (MCP = port+1) |
| `--dir` / `-d` | `.` | Répertoire parent |
| `--ref` | `main` | Branche/tag du template |

