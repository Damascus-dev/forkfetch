from __future__ import annotations

import json

from fetcher.database import Database
from fetcher.github_api import GitHubClient
from fetcher.scoring import score_repository
from fetcher.utils import utc_now_iso


class CacheService:
    def __init__(self, database: Database) -> None:
        self.database = database

    async def store_search(self, query: str, items: list[dict], total_count: int) -> list[dict]:
        fetched_at = utc_now_iso()
        enriched_items: list[dict] = []
        for item in items:
            repo = dict(item)
            repo["fetcher_score"] = score_repository(repo, query)
            repo["fetcher_fetched_at"] = fetched_at
            enriched_items.append(repo)

        enriched_items.sort(
            key=lambda repo: (repo["fetcher_score"], repo.get("stargazers_count", 0)),
            reverse=True,
        )

        await self.database.upsert_repositories(enriched_items)
        await self.database.record_search(
            query=query,
            repo_full_names=[repo["full_name"] for repo in enriched_items],
            total_count=total_count,
            searched_at=fetched_at,
        )
        return enriched_items

    async def refresh_latest_search(self, github: GitHubClient) -> list[dict]:
        latest = await self.database.latest_search()
        if latest is None:
            return []

        query = latest["query"]
        full_names = json.loads(latest["repo_full_names"])
        if not full_names:
            return []

        refreshed: list[dict] = []
        for full_name in full_names:
            repo = await github.get_repository(full_name)
            repo["fetcher_score"] = score_repository(repo, query)
            repo["fetcher_fetched_at"] = utc_now_iso()
            refreshed.append(repo)

        refreshed.sort(
            key=lambda repo: (repo["fetcher_score"], repo.get("stargazers_count", 0)),
            reverse=True,
        )
        await self.database.upsert_repositories(refreshed)
        await self.database.record_search(
            query=query,
            repo_full_names=[repo["full_name"] for repo in refreshed],
            total_count=latest["total_count"],
            searched_at=utc_now_iso(),
        )
        return refreshed
