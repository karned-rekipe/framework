from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree

from . import __version__
from .rename import EntityNames, apply_rename
from .scaffold import download_and_extract
from .updater import run_update

app = typer.Typer(
    name="arclith-cli",
    help="Scaffold [bold]arclith[/bold] hexagonal projects from the official template.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)
console = Console()


@app.command()
def new(
    entity: Annotated[
        str,
        typer.Argument(
            help="Entity name — any case accepted: [dim]Recipe[/dim], [dim]recipe_step[/dim], [dim]meal-plan[/dim]",
        ),
    ],
    project_name: Annotated[
        str,
        typer.Argument(help="Project directory name. Example: [dim]my-recipe-service[/dim]"),
    ],
    directory: Annotated[
        Path,
        typer.Option("--dir", "-d", help="Parent directory where the project will be created"),
    ] = Path("."),
    port: Annotated[
        int,
        typer.Option("--port", "-p", help="REST API port. MCP port will be port+1."),
    ] = 8000,
    repo_ref: Annotated[
        str,
        typer.Option("--ref", help="Git branch or tag of the _sample template"),
    ] = "main",
) -> None:
    """Create a new [bold]arclith[/bold] project scaffolded from the official [dim]_sample[/dim] template."""
    names = EntityNames.from_input(entity)
    target_dir = directory.resolve() / project_name

    if target_dir.exists():
        console.print(f"[red]✗[/red] Directory already exists: [bold]{target_dir}[/bold]")
        raise typer.Exit(1)

    console.print(
        Panel.fit(
            f"[bold blue]arclith-cli[/bold blue] [dim]v{__version__}[/dim]\n\n"
            f"  Entity   [bold green]{names.pascal}[/bold green]  [dim]({names.snake} / {names.upper})[/dim]\n"
            f"  Project  [bold]{project_name}[/bold]\n"
            f"  Target   [dim]{target_dir}[/dim]\n"
            f"  Ports    REST [bold]{port}[/bold]  ·  MCP [bold]{port + 1}[/bold]",
            border_style="blue",
            title="[bold]New project[/bold]",
        )
    )

    with console.status("[bold]Downloading template from GitHub…[/bold]"):
        try:
            download_and_extract(target_dir, ref=repo_ref)
        except Exception as exc:
            console.print(f"[red]✗ Download failed:[/red] {exc}")
            raise typer.Exit(1) from exc

    console.print("[green]✓[/green] Template extracted")

    with console.status("[bold]Renaming entity…[/bold]"):
        apply_rename(target_dir, names, project_name=project_name, port=port)

    console.print("[green]✓[/green] Rename complete")
    _print_summary(target_dir, project_name, port)


@app.command()
def update(
    ref: Annotated[
        str | None,
        typer.Option("--ref", help="Branche ou tag Git cible (défaut : main)"),
    ] = None,
) -> None:
    """Mettre à jour arclith-cli vers la dernière version depuis GitHub."""
    run_update(ref=ref)


@app.command()
def version() -> None:
    """Show the arclith-cli version."""
    console.print(f"arclith-cli [bold]{__version__}[/bold]")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _print_summary(target_dir: Path, project_name: str, port: int) -> None:
    tree = Tree(f"[bold green]{project_name}/[/bold green]")
    _build_tree(tree, target_dir, depth=0, max_depth=3)
    console.print()
    console.print(tree)
    console.print(
        Panel(
            f"[bold cyan]cd[/bold cyan] {target_dir}\n"
            f"[bold cyan]uv sync[/bold cyan]\n\n"
            f"[bold cyan]uv run python main.py[/bold cyan]"
            f"  [dim]# MODE=api → REST :{port}[/dim]\n"
            f"[bold cyan]MODE=mcp_http uv run python main.py[/bold cyan]"
            f"  [dim]# MCP :{port + 1}[/dim]",
            title="[bold blue]Next steps[/bold blue]",
            border_style="green",
        )
    )


def _build_tree(node: Tree, path: Path, depth: int, max_depth: int) -> None:
    if depth >= max_depth:
        return
    try:
        children = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name))
    except PermissionError:
        return
    for child in children:
        if child.name.startswith("."):
            continue
        label = f"[blue]{child.name}/[/blue]" if child.is_dir() else child.name
        branch = node.add(label)
        if child.is_dir():
            _build_tree(branch, child, depth + 1, max_depth)

