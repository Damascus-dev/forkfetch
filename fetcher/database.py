from __future__ import annotations

import json
import sqlite3
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS repos (
    id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    owner TEXT NOT NULL,
    description TEXT,
    html_url TEXT NOT NULL,
    language TEXT,
    stars INTEGER NOT NULL,
    open_issues INTEGER NOT NULL,
    archived INTEGER NOT NULL,
    pushed_at TEXT,
    score REAL NOT NULL,
    raw_json TEXT NOT NULL,
    fetched_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS search_history (
    id INTEGER PRIMARY KEY,
    query TEXT NOT NULL UNIQUE,
    repo_full_names TEXT NOT NULL,
    total_count INTEGER NOT NULL,
    searched_at TEXT NOT NULL
);
"""


class Database:
    def __init__(self, path: Path) -> None:
        self.path = path

    async def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as db:
            db.executescript(SCHEMA)
            db.commit()

    async def upsert_repositories(self, repositories: list[dict]) -> None:
        if not repositories:
            return

        with sqlite3.connect(self.path) as db:
            db.executemany(
                """
                INSERT INTO repos (
                    full_name, name, owner, description, html_url, language, stars,
                    open_issues, archived, pushed_at, score, raw_json, fetched_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(full_name) DO UPDATE SET
                    name = excluded.name,
                    owner = excluded.owner,
                    description = excluded.description,
                    html_url = excluded.html_url,
                    language = excluded.language,
                    stars = excluded.stars,
                    open_issues = excluded.open_issues,
                    archived = excluded.archived,
                    pushed_at = excluded.pushed_at,
                    score = excluded.score,
                    raw_json = excluded.raw_json,
                    fetched_at = excluded.fetched_at
                """,
                [
                    (
                        repo["full_name"],
                        repo["name"],
                        repo["owner"]["login"],
                        repo.get("description"),
                        repo["html_url"],
                        repo.get("language"),
                        int(repo.get("stargazers_count") or 0),
                        int(repo.get("open_issues_count") or 0),
                        1 if repo.get("archived") else 0,
                        repo.get("pushed_at"),
                        float(repo["fetcher_score"]),
                        json.dumps(repo),
                        repo["fetcher_fetched_at"],
                    )
                    for repo in repositories
                ],
            )
            db.commit()

    async def record_search(
        self,
        query: str,
        repo_full_names: list[str],
        total_count: int,
        searched_at: str,
    ) -> None:
        with sqlite3.connect(self.path) as db:
            db.execute(
                """
                INSERT INTO search_history (query, repo_full_names, total_count, searched_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(query) DO UPDATE SET
                    repo_full_names = excluded.repo_full_names,
                    total_count = excluded.total_count,
                    searched_at = excluded.searched_at
                """,
                (query, json.dumps(repo_full_names), total_count, searched_at),
            )
            db.commit()

    async def top_repositories(self, limit: int = 10) -> list[sqlite3.Row]:
        with sqlite3.connect(self.path) as db:
            db.row_factory = sqlite3.Row
            cursor = db.execute(
                """
                SELECT full_name, description, stars, language, pushed_at, score
                FROM repos
                ORDER BY score DESC, stars DESC
                LIMIT ?
                """,
                (limit,),
            )
            rows = cursor.fetchall()
            cursor.close()
            return rows

    async def latest_search(self) -> sqlite3.Row | None:
        with sqlite3.connect(self.path) as db:
            db.row_factory = sqlite3.Row
            cursor = db.execute(
                """
                SELECT query, repo_full_names, total_count, searched_at
                FROM search_history
                ORDER BY searched_at DESC
                LIMIT 1
                """
            )
            row = cursor.fetchone()
            cursor.close()
            return row

    async def repositories_by_full_names(self, full_names: list[str]) -> list[sqlite3.Row]:
        if not full_names:
            return []

        placeholders = ", ".join("?" for _ in full_names)
        with sqlite3.connect(self.path) as db:
            db.row_factory = sqlite3.Row
            cursor = db.execute(
                f"""
                SELECT full_name, description, stars, language, pushed_at, score
                FROM repos
                WHERE full_name IN ({placeholders})
                """,
                full_names,
            )
            rows = cursor.fetchall()
            cursor.close()
            order = {name: index for index, name in enumerate(full_names)}
            return sorted(rows, key=lambda row: order.get(row["full_name"], len(order)))
