from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_SOURCE_PASCAL = "Ingredient"
_SOURCE_SNAKE = "ingredient"
_SOURCE_UPPER = "INGREDIENT"

_TEXT_EXTENSIONS = {
    ".py", ".yaml", ".yml", ".toml", ".md", ".txt", ".json",
    ".cfg", ".ini", ".env", ".sh", ".rst",
}


@dataclass(frozen=True)
class EntityNames:
    pascal: str  # RecipeStep
    snake: str   # recipe_step
    upper: str   # RECIPE_STEP

    @classmethod
    def from_input(cls, raw: str) -> "EntityNames":
        pascal = _to_pascal(raw)
        snake = _to_snake(raw)
        return cls(pascal=pascal, snake=snake, upper=snake.upper())


def apply_rename(target_dir: Path, names: EntityNames, *, project_name: str, port: int) -> None:
    _rename_file_contents(target_dir, names)
    _rename_paths(target_dir, names)
    _patch_pyproject(target_dir, project_name)
    _patch_config(target_dir, project_name, port)


# ── Content replacement ───────────────────────────────────────────────────────

def _replace_in_text(text: str, names: EntityNames) -> str:
    # Order: most specific first to avoid partial overlap (UPPER before lower)
    return (
        text
        .replace(_SOURCE_UPPER, names.upper)
        .replace(_SOURCE_PASCAL, names.pascal)
        .replace(_SOURCE_SNAKE, names.snake)
    )


def _rename_file_contents(directory: Path, names: EntityNames) -> None:
    for path in directory.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in _TEXT_EXTENSIONS and path.suffix != "":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue
        new_text = _replace_in_text(text, names)
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")


# ── Path renaming ─────────────────────────────────────────────────────────────

def _rename_paths(directory: Path, names: EntityNames) -> None:
    # Deepest first so parent renames don't invalidate children
    candidates = sorted(
        directory.rglob("*"),
        key=lambda p: len(p.parts),
        reverse=True,
    )
    for path in candidates:
        if not path.exists():
            continue
        if not any(tok in path.name for tok in (_SOURCE_SNAKE, _SOURCE_PASCAL, _SOURCE_UPPER)):
            continue
        new_name = _replace_in_text(path.name, names)
        if new_name != path.name:
            path.rename(path.parent / new_name)


# ── pyproject.toml patching ───────────────────────────────────────────────────

def _patch_pyproject(target_dir: Path, project_name: str) -> None:
    p = target_dir / "pyproject.toml"
    if not p.exists():
        return
    text = p.read_text()
    # Update project name (first occurrence)
    text = re.sub(r'(?m)^name\s*=\s*"[^"]*"', f'name = "{project_name}"', text, count=1)
    # Remove [tool.uv.sources] block (editable arclith path)
    text = re.sub(
        r"\[tool\.uv\.sources\]\n(?:[^\[]*)",
        "",
        text,
        flags=re.DOTALL,
    )
    p.write_text(text.strip() + "\n")


# ── config.yaml patching ──────────────────────────────────────────────────────

def _patch_config(target_dir: Path, project_name: str, port: int) -> None:
    p = target_dir / "config.yaml"
    if not p.exists():
        return
    text = p.read_text()
    text = re.sub(r"(?m)(^  name:\s*).*$", rf"\g<1>{project_name}", text, count=1)
    text = re.sub(
        r'(?m)(^  description:\s*).*$',
        rf'\g<1>"{project_name} — built on arclith"',
        text,
        count=1,
    )
    text = re.sub(r"(?m)(^    db_name:\s*).*$", rf"\g<1>{project_name}", text, count=1)
    text = _replace_section_port(text, "api", port)
    text = _replace_section_port(text, "mcp", port + 1)
    p.write_text(text)


def _replace_section_port(text: str, section: str, new_port: int) -> str:
    pattern = re.compile(
        rf"(^{re.escape(section)}:.*?)(^\s+port:\s*)\d+",
        re.MULTILINE | re.DOTALL,
    )
    return pattern.sub(lambda m: f"{m.group(1)}{m.group(2)}{new_port}", text, count=1)


# ── Case converters ───────────────────────────────────────────────────────────

def _to_pascal(raw: str) -> str:
    if "_" in raw or "-" in raw:
        return "".join(w.capitalize() for w in re.split(r"[_\-]", raw) if w)
    return raw[0].upper() + raw[1:] if raw else raw


def _to_snake(raw: str) -> str:
    if "_" in raw:
        return raw.lower()
    if "-" in raw:
        return raw.replace("-", "_").lower()
    # PascalCase / camelCase → snake_case
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", raw)
    s = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", s)
    return s.lower()

