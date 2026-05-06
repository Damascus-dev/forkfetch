# Fetcher Implementation Plan

## Scope

Build the MVP described in `fetcher_mvp_spec.md` with four user-facing commands:

- `ffetch search "query"`
- `ffetch top`
- `ffetch refresh`
- `ffetch clone owner/repo`

## Design

1. CLI layer
   - Use Typer for command registration and argument parsing.
   - Use Rich for tables, panels, and JSON output.

2. GitHub integration
   - Implement an async `GitHubClient` with:
     - repository search
     - single-repo fetch for refresh
   - Support optional personal access token from config.

3. Ranking
   - Score each repository with:
     - log-scaled stars
     - freshness bonus from `pushed_at`
     - keyword match bonus from name, description, and topics
     - penalties for archived repos and weak issue ratio

4. Caching
   - Store repositories in SQLite.
   - Track latest search query and ordered result set in `search_history`.
   - Refresh re-fetches the most recent cached search.

5. Cloning
   - Shell out to `git clone`.
   - Return a clear error when cloning fails.

## Module Responsibilities

- `fetcher/main.py`: CLI entrypoints and rendering
- `fetcher/github_api.py`: GitHub API client and error handling
- `fetcher/scoring.py`: repository ranking
- `fetcher/database.py`: schema and SQLite access
- `fetcher/cache.py`: cache orchestration and refresh flow
- `fetcher/clone.py`: cloning logic
- `fetcher/config.py`: config and writable path resolution
- `fetcher/utils.py`: time parsing/helpers

## Execution Order

1. Scaffold package and packaging metadata.
2. Implement configuration and writable data directory handling.
3. Implement database schema and cache writes.
4. Implement GitHub API integration and ranking.
5. Wire CLI commands and terminal rendering.
6. Verify help/config/top locally.
7. Verify search/refresh against the live GitHub API when dependencies and network are available.
