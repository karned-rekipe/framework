# framework

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

