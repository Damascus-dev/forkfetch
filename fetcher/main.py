from __future__ import annotations

import asyncio
from pathlib import Path

import click
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from fetcher.cache import CacheService
from fetcher.clone import clone_repository
from fetcher.config import clear_github_token, load_settings, save_github_token
from fetcher.database import Database
from fetcher.github_api import GitHubApiError, GitHubClient
from fetcher.utils import parse_github_datetime


app = typer.Typer(
    help="Smart GitHub repository discovery CLI. Run `ffetch` with no command for interactive mode.",
    invoke_without_command=True,
    no_args_is_help=False,
)
console = Console()


def _short_description(value: str | None, limit: int = 72) -> str:
    text = (value or "").strip()
    if not text:
        return ""
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def render_repositories(title: str, repositories: list[dict]) -> None:
    if not repositories:
        console.print(Panel("No repositories found.", title=title))
        return

    show_description = sum(1 for repo in repositories if (repo.get("description") or "").strip()) >= 2

    table = Table(title=title, expand=True, pad_edge=False)
    table.add_column("#", justify="right", no_wrap=True, style="cyan", width=3)
    table.add_column("Repository", style="bold cyan", no_wrap=True, overflow="ellipsis", min_width=24, max_width=34)
    if show_description:
        table.add_column("Description", no_wrap=True, overflow="ellipsis", min_width=18, max_width=36)
    table.add_column("Stars", justify="right", no_wrap=True, width=7)
    table.add_column("Lang", no_wrap=True, overflow="ellipsis", width=10)
    table.add_column("Updated", no_wrap=True, width=10)
    table.add_column("Score", justify="right", no_wrap=True, style="green", width=7)

    for index, repo in enumerate(repositories, start=1):
        pushed_at = parse_github_datetime(repo.get("pushed_at"))
        updated = pushed_at.date().isoformat() if pushed_at else "unknown"
        stars = str(repo.get("stargazers_count", repo.get("stars", 0)))
        score = f'{repo.get("fetcher_score", repo.get("score", 0.0)):.2f}'
        language = repo.get("language") or "-"
        description = _short_description(repo.get("description"), limit=80)
        row = [
            str(index),
            repo["full_name"],
        ]
        if show_description:
            row.append(description)
        row.extend([stars, language, updated, score])
        table.add_row(*row)

    console.print(table)


async def bootstrap() -> tuple[Database, CacheService, GitHubClient]:
    settings = load_settings()
    database = Database(settings.database_path)
    await database.initialize()
    cache = CacheService(database)
    github = GitHubClient(token=settings.github_token)
    return database, cache, github


async def bootstrap_database() -> Database:
    settings = load_settings()
    database = Database(settings.database_path)
    await database.initialize()
    return database


async def run_search(query: str, limit: int) -> None:
    database, cache, github = await bootstrap()
    try:
        response = await github.search_repositories(query, per_page=limit)
        repos = await cache.store_search(query, response.items, response.total_count)
    finally:
        await github.aclose()

    render_repositories(f'Search: "{query}"', repos)
    console.print(f"Cached {len(repos)} repos in {database.path}")


async def run_top(limit: int) -> None:
    database = await bootstrap_database()
    rows = await database.top_repositories(limit)
    repos = [dict(row) for row in rows]
    render_repositories("Top Cached Repositories", repos)


async def run_refresh() -> None:
    _, cache, github = await bootstrap()
    try:
        repos = await cache.refresh_latest_search(github)
    finally:
        await github.aclose()
    render_repositories("Refreshed Latest Search", repos)


def show_config_summary() -> None:
    settings = load_settings()
    auth_mode = "token" if settings.github_token else "public"
    api_mode = "authenticated GitHub API" if settings.github_token else "public GitHub API"
    payload = {
        "config_path": str(settings.config_path),
        "database_path": str(settings.database_path),
        "auth_mode": auth_mode,
        "api_mode": api_mode,
        "github_token_configured": bool(settings.github_token),
    }
    console.print_json(data=payload)


def _prompt_text(label: str, default: str | None = None, hide_input: bool = False) -> str | None:
    try:
        return typer.prompt(label, default=default, hide_input=hide_input).strip()
    except (click.Abort, KeyboardInterrupt, EOFError):
        console.print("[yellow]Canceled. Back to menu.[/yellow]")
        return None


def _prompt_int(label: str, default: int) -> int | None:
    value = _prompt_text(label, default=str(default))
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        console.print("[red]Expected a number.[/red]")
        return None


def interactive_menu() -> None:
    while True:
        settings = load_settings()
        auth_mode = "GitHub token" if settings.github_token else "Public API"
        api_mode = "Authenticated GitHub API" if settings.github_token else "Public GitHub API"
        console.print(Panel(
            "\n".join(
                [
                    f"Auth: {auth_mode}",
                    f"API: {api_mode}",
                    "1. Search repositories",
                    "2. Show top cached repositories",
                    "3. Refresh latest search",
                    "4. Clone repository",
                    "5. Connect GitHub token",
                    "6. Use free public API",
                    "7. Show config",
                    "0. Exit",
                    "",
                    "After each action, ffetch returns to this menu.",
                    "Ctrl+C in a prompt: cancel action",
                    "Ctrl+C here in the menu: exit ffetch",
                ]
            ),
            title="ffetch",
        ))

        try:
            choice = typer.prompt("*", default="", show_default=False).strip()
        except (click.Abort, KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Exiting ffetch.[/yellow]")
            return

        if not choice:
            console.print("[yellow]Enter a menu number.[/yellow]")
            continue

        try:
            if choice == "1":
                query = _prompt_text("Search query")
                if query is None:
                    continue
                limit = _prompt_int("Result limit", 10)
                if limit is None:
                    continue
                asyncio.run(run_search(query, limit))
            elif choice == "2":
                limit = _prompt_int("Result limit", 10)
                if limit is None:
                    continue
                asyncio.run(run_top(limit))
            elif choice == "3":
                asyncio.run(run_refresh())
            elif choice == "4":
                repository = _prompt_text("Repository (owner/name)")
                if repository is None:
                    continue
                destination = _prompt_text("Destination directory", default="")
                if destination is None:
                    continue
                path = clone_repository(repository, Path(destination) if destination else None)
                console.print(f"Cloned {repository} into {path}")
            elif choice == "5":
                token = _prompt_text("GitHub token", hide_input=True)
                if token is None:
                    continue
                path = save_github_token(token)
                console.print(f"Saved token to {path}")
            elif choice == "6":
                path = clear_github_token()
                console.print(f"Using public GitHub API. Cleared token in {path}")
            elif choice == "7":
                show_config_summary()
            elif choice == "0":
                return
            else:
                console.print("[yellow]Unknown option.[/yellow]")
        except GitHubApiError as exc:
            console.print(f"[red]{exc}[/red]")
        except RuntimeError as exc:
            console.print(f"[red]{exc}[/red]")


@app.callback(invoke_without_command=True)
def root(ctx: typer.Context) -> None:
    """Run the interactive CLI when no subcommand is provided."""
    if ctx.invoked_subcommand is None:
        interactive_menu()


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query to send to GitHub."),
    limit: int = typer.Option(10, min=1, max=50, help="Number of repositories to fetch."),
) -> None:
    """Search GitHub repositories."""
    try:
        asyncio.run(run_search(query, limit))
    except GitHubApiError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc


@app.command()
def top(
    limit: int = typer.Option(10, min=1, max=50, help="Number of cached repositories to show."),
) -> None:
    """Show top ranked cached repositories."""
    asyncio.run(run_top(limit))


@app.command()
def refresh() -> None:
    """Refresh the latest cached search from GitHub."""
    try:
        asyncio.run(run_refresh())
    except GitHubApiError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc


@app.command()
def clone(
    repository: str = typer.Argument(..., help="Repository in owner/name format."),
    destination: Path | None = typer.Option(None, help="Destination directory."),
) -> None:
    """Clone a repository directly from GitHub."""
    try:
        path = clone_repository(repository, destination)
    except RuntimeError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc

    console.print(f"Cloned {repository} into {path}")


@app.command()
def config() -> None:
    """Show config and database locations."""
    show_config_summary()


if __name__ == "__main__":
    app()
